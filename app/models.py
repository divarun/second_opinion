from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class ConfidenceLevel(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"

class DocumentSection(BaseModel):
    heading: str
    content: str
    confidence_weight: str = "medium"  # high, medium, low

class ParsedDocument(BaseModel):
    sections: List[DocumentSection]

class Assumption(BaseModel):
    text: str
    source_section: str
    confidence: ConfidenceLevel

class FailurePatternMatch(BaseModel):
    pattern_id: str
    name: str
    confidence: ConfidenceLevel
    match_strength: Optional[float] = None  # 0.0 to 1.0
    evidence: List[str]
    trigger_conditions: List[str]
    why_subtle: List[str]
    impact_surface: List[str]  # Derived from pattern metadata
    discussion_questions: List[str]

class ContextualMetadata(BaseModel):
    expected_scale_qps: Optional[str] = None
    expected_data_size: Optional[str] = None
    critical_slos_latency: Optional[str] = None
    critical_slos_availability: Optional[str] = None
    known_dependencies: Optional[str] = None

class SecondOpinionReport(BaseModel):
    overall_risk: ConfidenceLevel
    primary_concern: Optional[str]
    why_this_matters: Optional[str] = None
    summary: str
    confidence_note: str = "Confidence reflects similarity to known failure patterns, not probability."
    failure_modes: List[FailurePatternMatch]
    assumptions: List[Assumption]
    assumptions_note: str = "These assumptions are inferred from the design and are not validated."
    ruled_out: List[str]
    ruled_out_note: str = "Reviewed and deprioritized based on the provided design:"
    unknowns: List[str] = []  # Known unknowns / not evaluated
    version_info: Optional[dict] = None  # Pattern/prompt/model versions
    document_sections: Optional[List[str]] = None  # List of section headings from input document