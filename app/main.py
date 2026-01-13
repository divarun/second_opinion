"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pathlib import Path
import httpx

from app.api import router
from app.config import settings
from app.logger import logger
from app.patterns import FailurePatternLibrary


# Initialize FastAPI app
app = FastAPI(title="Second Opinion MVP")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Rate limiting is handled by slowapi exception handler


# Add CORS middleware if origins are configured
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {settings.cors_origins}")

# Include router
app.include_router(router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return JSONResponse({
        "status": "healthy",
        "service": "second_opinion"
    })


@app.on_event("startup")
async def validate_config():
    """Validate configuration on startup."""
    logger.info("Starting Second Opinion application...")
    
    # Validate Ollama configuration
    if not settings.ollama_model_name:
        logger.error("OLLAMA_MODEL_NAME is not configured")
        raise ValueError("OLLAMA_MODEL_NAME must be set in environment variables")
    
    # Check if pattern library exists
    pattern_path = Path(settings.pattern_library_path)
    if not pattern_path.exists():
        logger.error(f"Pattern library not found: {settings.pattern_library_path}")
        raise FileNotFoundError(f"Pattern library not found: {settings.pattern_library_path}")
    
    # Try to load pattern library to validate it
    try:
        library = FailurePatternLibrary(settings.pattern_library_path)
        logger.info(f"Pattern library validated: {len(library.all())} patterns loaded")
    except Exception as e:
        logger.error(f"Failed to load pattern library: {e}")
        raise
    
    # Check Ollama connectivity (non-blocking check)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            if response.status_code == 200:
                logger.info(f"Ollama connection verified at {settings.ollama_base_url}")
            else:
                logger.warning(f"Ollama returned status {response.status_code}")
    except Exception as e:
        logger.warning(f"Could not verify Ollama connection: {e}. Continuing anyway...")
    
    logger.info("Configuration validation complete")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down Second Opinion application...")
