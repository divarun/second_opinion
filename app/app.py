"""
Second Opinion - Simplified Pre-mortem Review Tool
Main FastAPI application with all routes and core logic
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import os

from analyzer import DesignAnalyzer
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Second Opinion",
    description="Pre-mortem review tool for engineering design documents",
    version="2.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize analyzer
analyzer = DesignAnalyzer()


# Request/Response Models
class AnalysisRequest(BaseModel):
    """Request model for document analysis"""
    document: str = Field(..., description="Design document text")
    context: Optional[dict] = Field(default={}, description="Optional context (scale, SLOs, dependencies)")


class AnalysisResponse(BaseModel):
    """Response model containing analysis results"""
    failure_modes: List[dict]
    implicit_assumptions: List[str]
    ruled_out_risks: List[str]
    known_unknowns: List[str]
    summary: str


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main application page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_document(request: AnalysisRequest):
    """
    Analyze a design document for potential failure modes

    This endpoint accepts a design document and optional context,
    then returns a comprehensive pre-mortem analysis.
    """
    try:
        # Perform analysis
        results = await analyzer.analyze(
            document=request.document,
            context=request.context
        )

        return AnalysisResponse(**results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/upload")
async def upload_file(
        file: UploadFile = File(...),
        context_scale: Optional[str] = Form(None),
        context_slos: Optional[str] = Form(None),
        context_dependencies: Optional[str] = Form(None)
):
    """
    Upload and analyze a design document file

    Supports: .md, .txt, .rst, .adoc files
    """
    # Validate file type
    allowed_extensions = {'.md', '.txt', '.rst', '.adoc'}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Read file content
    content = await file.read()
    try:
        document_text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    # Build context
    context = {}
    if context_scale:
        context['scale'] = context_scale
    if context_slos:
        context['slos'] = context_slos
    if context_dependencies:
        context['dependencies'] = context_dependencies

    # Analyze
    try:
        results = await analyzer.analyze(
            document=document_text,
            context=context
        )
        return JSONResponse(content=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/patterns")
async def list_patterns():
    """List all available failure patterns"""
    return {
        "patterns": [
            {
                "id": pattern.id,
                "name": pattern.name,
                "description": pattern.description,
                "category": pattern.category
            }
            for pattern in analyzer.patterns
        ]
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = await analyzer.check_llm_health()

    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama": "connected" if ollama_status else "disconnected",
        "model": settings.ollama_model
    }


# Run application
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )