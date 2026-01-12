from fastapi import APIRouter, Form, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.ingestion import parse_document
from app.assumptions import extract_assumptions
from app.matcher import match_patterns
from app.patterns import FailurePatternLibrary
from app.report import build_report
from app.synthesis import synthesize_summary
from app.file_processor import extract_text_from_file

router = APIRouter()
templates = Jinja2Templates(directory="app/static")
patterns = FailurePatternLibrary("data/failure_patterns.json")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "report": None, "loading": False, "error": None})

@router.post("/submit", response_class=HTMLResponse)
async def submit(
    request: Request,
    document: str = Form(None),
    file: Optional[UploadFile] = File(None),
    expected_scale_qps: str = Form(None),
    expected_data_size: str = Form(None),
    critical_slos_latency: str = Form(None),
    critical_slos_availability: str = Form(None),
    known_dependencies: str = Form(None)
):
    # Determine document source: file takes precedence over text input
    document_text = ""
    
    if file and file.filename:
        from app.file_processor import is_supported_file
        if not is_supported_file(file.filename):
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
            return templates.TemplateResponse(
                "index.html", 
                {
                    "request": request, 
                    "report": None, 
                    "loading": False,
                    "error": e.detail
                }
            )
        except Exception as e:
            return templates.TemplateResponse(
                "index.html", 
                {
                    "request": request, 
                    "report": None, 
                    "loading": False,
                    "error": f"Error reading file: {str(e)}"
                }
            )
    elif document:
        document_text = document
    else:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "report": None,
                "loading": False,
                "error": "Please provide either a file upload or paste text in the text area."
            }
        )
    
    # Combine document with contextual metadata if provided
    full_document = document_text
    if any([expected_scale_qps, expected_data_size, critical_slos_latency, critical_slos_availability, known_dependencies]):
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
    
    try:
        parsed = parse_document(full_document)
        assumptions = extract_assumptions(parsed)
        matches = match_patterns(parsed, patterns, assumptions)
    except Exception as e:
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
    
    try:
        report = build_report(
            matches, 
            assumptions, 
            parsed,
            full_document,
            patterns,
            contextual_metadata
        )
        return templates.TemplateResponse("index.html", {"request": request, "report": report, "loading": False, "error": None})
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "report": None,
                "loading": False,
                "error": f"Error generating report: {str(e)}"
            }
        )
