"""
Configuration Management
Centralized settings using Pydantic BaseSettings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Ollama Configuration
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: int = 120

    # Analysis Configuration
    max_document_size: int = 50000  # characters
    confidence_threshold: float = 0.6
    max_failure_modes: int = 10

    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()