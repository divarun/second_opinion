"""
Versioning System
Tracks versions of patterns, prompts, models, and confidence thresholds for reproducibility.
"""
import os
import hashlib
import json
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_pattern_version(pattern_path: str = "data/failure_patterns.json") -> str:
    """Get version hash of failure patterns file."""
    try:
        content = Path(pattern_path).read_text()
        return hashlib.sha256(content.encode()).hexdigest()[:8]
    except Exception:
        return "unknown"

def get_model_version() -> str:
    """Get model version from environment."""
    model_name = os.getenv("OLLAMA_MODEL_NAME", "unknown")
    # Could be enhanced to get actual model version from Ollama API
    return model_name

def get_prompt_hash(prompt: str) -> str:
    """Get hash of a prompt for versioning."""
    return hashlib.sha256(prompt.encode()).hexdigest()[:8]

def get_version_info() -> Dict:
    """Get complete version information for a report."""
    return {
        "pattern_version": get_pattern_version(),
        "model_name": get_model_version(),
        "temperature": 0,  # Fixed for determinism
        "confidence_thresholds": {
            "high": 3,  # signals
            "medium": 1  # signals
        }
    }
