"""Pydantic schemas for API input validation."""
from pydantic import BaseModel, Field, validator
from typing import Optional


class DocumentSubmission(BaseModel):
    """Schema for document submission with validation."""
    
    document: Optional[str] = Field(
        None,
        max_length=1_000_000,  # 1MB limit for text
        description="Document text content"
    )
    expected_scale_qps: Optional[str] = Field(
        None,
        max_length=100,
        description="Expected scale in QPS"
    )
    expected_data_size: Optional[str] = Field(
        None,
        max_length=100,
        description="Expected data size"
    )
    critical_slos_latency: Optional[str] = Field(
        None,
        max_length=100,
        description="Critical SLOs for latency"
    )
    critical_slos_availability: Optional[str] = Field(
        None,
        max_length=100,
        description="Critical SLOs for availability"
    )
    known_dependencies: Optional[str] = Field(
        None,
        max_length=500,
        description="Known dependencies"
    )
    
    @validator('document')
    def validate_document(cls, v):
        """Validate document is not empty if provided."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Document cannot be empty")
        return v
