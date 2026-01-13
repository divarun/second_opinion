"""Manages the library of failure patterns.

Loads patterns from JSON file and provides access methods.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from app.logger import logger


class FailurePatternLibrary:
    """Manages the library of failure patterns.
    
    Loads patterns from JSON file and provides access methods.
    
    Args:
        path: Path to the JSON file containing failure patterns.
        
    Raises:
        FileNotFoundError: If pattern file doesn't exist.
        ValueError: If pattern file is invalid JSON or empty.
    """
    
    def __init__(self, path: str):
        """Initialize the pattern library from a JSON file."""
        try:
            pattern_path = Path(path)
            if not pattern_path.exists():
                raise FileNotFoundError(f"Pattern library not found: {path}")
            
            with open(pattern_path, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
            
            if not isinstance(self.patterns, list):
                raise ValueError(f"Pattern library must be a list, got {type(self.patterns)}")
            
            if not self.patterns:
                raise ValueError("Pattern library is empty")
            
            logger.info(f"Loaded {len(self.patterns)} failure patterns from {path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in pattern library {path}: {e}")
            raise ValueError(f"Invalid JSON in pattern library: {e}")
        except Exception as e:
            logger.error(f"Error loading pattern library from {path}: {e}", exc_info=True)
            raise

    def all(self) -> List[Dict[str, Any]]:
        """Return all failure patterns.
        
        Returns:
            List of pattern dictionaries.
        """
        return self.patterns
