"""Utility functions for processing uploaded files."""
from fastapi import UploadFile, HTTPException
import io

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from an uploaded file.
    Supports: .md, .txt, .rst, .adoc, and plain text files.
    
    Raises:
        HTTPException: If file is too large or cannot be read
    """
    # Get file extension
    filename = file.filename or ""
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    # Decode as text (try UTF-8, fallback to latin-1)
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = content.decode('latin-1')
        except UnicodeDecodeError:
            # Last resort: replace errors
            text = content.decode('utf-8', errors='replace')
    
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="File appears to be empty or contains no readable text"
        )
    
    # For markdown and other text formats, return as-is
    # The ingestion layer will handle parsing
    return text

def get_supported_extensions() -> list:
    """Return list of supported file extensions."""
    return ['.md', '.markdown', '.txt', '.rst', '.adoc', '.asciidoc', '.text']

def is_supported_file(filename: str) -> bool:
    """Check if file extension is supported."""
    if not filename or '.' not in filename:
        return False
    extension = '.' + filename.split('.')[-1].lower()
    return extension in get_supported_extensions()
