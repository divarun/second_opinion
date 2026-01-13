"""API routes for Second Opinion."""
import asyncio
from fastapi import APIRouter, Form, Request, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.ingestion import parse_document
from app.assumptions import extract_assumptions
from app.matcher import match_patterns
from app.patterns import FailurePatternLibrary
from app.report import build_report
from app.file_processor import extract_text_from_file, is_supported_file
from app.config import settings
from app.logger import logger
from app.llm import LLMError


router = APIRouter()

# Dependency injection for pattern library
def get_pattern_library() -> FailurePatternLibrary:
    """Get pattern library instance (cached)."""
    return FailurePatternLibrary(settings.pattern_library_path)


# Dependency injection for templates
def get_templates() -> Jinja2Templates:
    """Get Jinja2 templates instance."""
    return Jinja2Templates(directory="app/static", autoescape=True)


@router.get("/", response_class=HTMLResponse)
def index(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    """Render the main index page."""
    logger.info("Index page requested")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "report": None,
            "loading": False,
            "error": None
        }
    )


@router.post("/submit", response_class=HTMLResponse)
async def submit(
    request: Request,
    document: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    expected_scale_qps: Optional[str] = Form(None),
    expected_data_size: Optional[str] = Form(None),
    critical_slos_latency: Optional[str] = Form(None),
    critical_slos_availability: Optional[str] = Form(None),
    known_dependencies: Optional[str] = Form(None),
    patterns: FailurePatternLibrary = Depends(get_pattern_library),
    templates: Jinja2Templates = Depends(get_templates)
):
    """
    Submit a design document for analysis.
    
    Accepts either a file upload or text input. Processes the document
    and returns a pre-mortem review report.
    """
    logger.info(f"Document submission received from {get_remote_address(request)}")
    
    # Validate input - at least one input method required
    if not file and not document:
        logger.warning("Submission rejected: no file or text provided")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "report": None,
                "loading": False,
                "error": "Please provide either a file upload or paste text in the text area."
            }
        )
    
    # Validate text input length if provided
    if document and len(document) > 1_000_000:
        logger.warning(f"Submission rejected: text too long ({len(document)} chars)")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "report": None,
                "loading": False,
                "error": "Document text is too large. Maximum size is 1MB."
            }
        )
    
    # Determine document source: file takes precedence over text input
    document_text = ""
    
    try:
        if file and file.filename:
            if not is_supported_file(file.filename):
                logger.warning(f"Unsupported file type: {file.filename}")
                return templates.TemplateResponse(
                    "index.html",
                    {
                        "request": request,
                        "report": None,
                        "loading": False,
                        "error": f"Unsupported file type. Supported formats: .md, .txt, .rst, .adoc, .text"
                    }
                )
            
            try:
                document_text = await extract_text_from_file(file)
            except HTTPException as e:
                logger.error(f"File processing error: {e.detail}")
                return templates.TemplateResponse(
                    "index.html",
                    {
                        "request": request,
                        "report": None,
                        "loading": False,
                        "error": e.detail
                    }
                )
        elif document:
            document_text = document.strip()
            if not document_text:
                logger.warning("Submission rejected: empty text document")
                return templates.TemplateResponse(
                    "index.html",
                    {
                        "request": request,
                        "report": None,
                        "loading": False,
                        "error": "Document text cannot be empty."
                    }
                )
        
        # Combine document with contextual metadata if provided
        full_document = document_text
        if any([expected_scale_qps, expected_data_size, critical_slos_latency, 
                critical_slos_availability, known_dependencies]):
            metadata_section = "\n\n## Contextual Metadata\n"
            if expected_scale_qps:
                metadata_section += f"Expected Scale (QPS): {expected_scale_qps}\n"
            if expected_data_size:
                metadata_section += f"Expected Data Size: {expected_data_size}\n"
            if critical_slos_latency:
                metadata_section += f"Critical SLOs (Latency): {critical_slos_latency}\n"
            if critical_slos_availability:
                metadata_section += f"Critical SLOs (Availability): {critical_slos_availability}\n"
            if known_dependencies:
                metadata_section += f"Known Dependencies: {known_dependencies}\n"
            full_document = document_text + metadata_section
        
        # Process document with timeout
        try:
            parsed, assumptions, matches = await asyncio.wait_for(
                _process_document(full_document, patterns),
                timeout=settings.api_request_timeout
            )
        except asyncio.TimeoutError:
            logger.error("Request timeout during document processing")
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "report": None,
                    "loading": False,
                    "error": "Request timeout. The document may be too large or processing took too long."
                }
            )
        except (ValueError, AttributeError) as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "report": None,
                    "loading": False,
                    "error": f"Error processing document: {str(e)}"
                }
            )
        
        # Prepare contextual metadata for report building
        contextual_metadata = {
            "expected_scale_qps": expected_scale_qps,
            "expected_data_size": expected_data_size,
            "critical_slos_latency": critical_slos_latency,
            "critical_slos_availability": critical_slos_availability,
            "known_dependencies": known_dependencies
        }
        
        # Build report with timeout
        try:
            report = await asyncio.wait_for(
                build_report(
                    matches,
                    assumptions,
                    parsed,
                    full_document,
                    patterns,
                    contextual_metadata
                ),
                timeout=settings.api_request_timeout
            )
            logger.info(f"Report generated successfully with {len(matches)} failure modes")
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "report": report,
                    "loading": False,
                    "error": None
                }
            )
        except asyncio.TimeoutError:
            logger.error("Request timeout during report generation")
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "report": None,
                    "loading": False,
                    "error": "Request timeout during report generation."
                }
            )
        except LLMError as e:
            logger.error(f"LLM error during report generation: {e}")
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "report": None,
                    "loading": False,
                    "error": "Error generating report. Please ensure Ollama is running and the model is available."
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error generating report: {e}", exc_info=True)
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "report": None,
                    "loading": False,
                    "error": f"Error generating report: {str(e)}"
                }
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in submit endpoint: {e}", exc_info=True)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "report": None,
                "loading": False,
                "error": "An unexpected error occurred. Please try again."
            }
        )


async def _process_document(full_document: str, patterns: FailurePatternLibrary):
    """Process document: parse, extract assumptions, and match patterns.
    
    This is a helper function that can be wrapped with timeout.
    """
    parsed = parse_document(full_document)
    assumptions = await extract_assumptions(parsed)
    matches = match_patterns(parsed, patterns, assumptions)
    return parsed, assumptions, matches
