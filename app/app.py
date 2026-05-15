"""
Second Opinion - Pre-mortem Review Tool
Main FastAPI application with all routes and core logic
"""
import asyncio
import io
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request
import uvicorn

from app.analyzer import DesignAnalyzer
from app.config import settings

BASE_DIR = Path(__file__).parent

analyzer = DesignAnalyzer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await analyzer.llm.close()


app = FastAPI(
    title="Second Opinion",
    description="Pre-mortem review tool for engineering design documents",
    version="2.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Request/Response Models
class AnalysisRequest(BaseModel):
    document: str = Field(..., description="Design document text")
    context: Optional[dict] = Field(default={}, description="Optional context (scale, SLOs, dependencies)")


class AnalysisResponse(BaseModel):
    failure_modes: List[dict]
    implicit_assumptions: List[str]
    ruled_out_risks: List[str]
    known_unknowns: List[str]
    summary: str


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_document(request: AnalysisRequest):
    """Analyze a design document — non-streaming version"""
    try:
        results = await analyzer.analyze(document=request.document, context=request.context)
        return AnalysisResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/stream")
async def analyze_stream(request: AnalysisRequest):
    """Analyze a design document with Server-Sent Events for live progress"""
    queue: asyncio.Queue = asyncio.Queue()

    async def run_analysis():
        async def on_progress(step: str, data: Optional[dict] = None):
            await queue.put({"type": "progress", "step": step, "data": data})

        try:
            results = await analyzer.analyze(
                document=request.document,
                context=request.context,
                on_progress=on_progress,
            )
            await queue.put({"type": "complete", "results": results})
        except Exception as e:
            await queue.put({"type": "error", "message": str(e)})
        finally:
            await queue.put(None)  # sentinel

    asyncio.create_task(run_analysis())

    async def event_stream():
        while True:
            item = await queue.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    context_scale: Optional[str] = Form(None),
    context_slos: Optional[str] = Form(None),
    context_dependencies: Optional[str] = Form(None),
):
    """
    Upload and analyze a design document file.
    Supports: .md, .txt, .rst, .adoc, .pdf
    """
    allowed_extensions = {".md", ".txt", ".rst", ".adoc", ".pdf"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(allowed_extensions))}",
        )

    content = await file.read()

    if file_ext == ".pdf":
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(content))
            pages_text = [page.extract_text() for page in reader.pages]
            document_text = "\n\n".join(t for t in pages_text if t)
            if not document_text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be scanned or image-only.")
        except ImportError:
            raise HTTPException(status_code=500, detail="PDF support requires pypdf. Run: pip install pypdf")
    else:
        try:
            document_text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    context = {}
    if context_scale:
        context["scale"] = context_scale
    if context_slos:
        context["slos"] = context_slos
    if context_dependencies:
        context["dependencies"] = context_dependencies

    try:
        results = await analyzer.analyze(document=document_text, context=context)
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
                "category": pattern.category,
            }
            for pattern in analyzer.patterns
        ]
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    llm_ok = await analyzer.check_llm_health()
    return {
        "status": "healthy" if llm_ok else "degraded",
        "provider": settings.llm_provider,
        "model": settings.anthropic_model if settings.llm_provider == "anthropic" else settings.ollama_model,
        "llm": "connected" if llm_ok else "disconnected",
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
