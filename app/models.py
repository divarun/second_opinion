"""
Data Models
Simplified Pydantic models for analysis results
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for pattern matching"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PatternCategory(str, Enum):
    """Categories of failure patterns"""
    LOAD = "load"
    DEPENDENCY = "dependency"
    DATA = "data"
    TIMING = "timing"
    RESOURCE = "resource"
    DISTRIBUTED = "distributed"


class FailurePattern(BaseModel):
    """Definition of a distributed systems failure pattern"""
    id: str
    name: str
    description: str
    category: PatternCategory
    indicators: List[str] = Field(default_factory=list)
    why_easy_to_miss: str = ""

    class Config:
        use_enum_values = True


class Finding(BaseModel):
    """A matched failure mode from analysis"""
    pattern_id: str
    pattern_name: str
    confidence: ConfidenceLevel
    match_score: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    trigger_conditions: List[str] = Field(default_factory=list)
    why_easy_to_miss: str = ""
    discussion_questions: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    failure_modes: List[Finding] = Field(default_factory=list)
    implicit_assumptions: List[str] = Field(default_factory=list)
    ruled_out_risks: List[str] = Field(default_factory=list)
    known_unknowns: List[str] = Field(default_factory=list)
    summary: str = ""