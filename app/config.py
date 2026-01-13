"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Configuration
    ollama_model_name: str
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: float = 30.0
    
    # LLM Configuration
    llm_system_prompt: Optional[str] = None
    llm_temperature: float = 0.0
    llm_max_retries: int = 3
    llm_retry_delay_min: float = 2.0
    llm_retry_delay_max: float = 10.0
    
    # File Processing
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    pattern_library_path: str = "data/failure_patterns.json"
    
    # API Configuration
    api_rate_limit: str = "5/minute"
    api_request_timeout: float = 300.0  # 5 minutes
    
    # Logging
    log_level: str = "INFO"
    
    # CORS (if needed)
    cors_origins: list[str] = []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
