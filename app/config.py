"""
Configuration Management
Centralized settings using Pydantic BaseSettings
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # LLM Provider — "ollama" or "anthropic"
    llm_provider: str = "ollama"

    # Ollama Configuration
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: int = 120

    # Anthropic Configuration
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Analysis Configuration
    max_document_size: int = 50000  # characters
    confidence_threshold: float = 0.6
    max_failure_modes: int = 10

    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
