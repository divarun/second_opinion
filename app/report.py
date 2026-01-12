from app.models import SecondOpinionReport, ConfidenceLevel, ParsedDocument
from app.llm import call_llm
from app.prompts import get_why_this_matters_prompt
from app.ruled_out import determine_ruled_out_risks
from app.unknowns import detect_unknowns
from app.versioning import get_version_info
from app.patterns import FailurePatternLibrary

def generate_why_this_matters(primary_concern: str, failure_modes) -> str:
    """Generate explanation of why the primary concern matters."""
    if not primary_concern or not failure_modes:
        return None
    
    primary_mode = next((m for m in failure_modes if m.name == primary_concern), None)
    if not primary_mode:
        return None
    
    prompt = get_why_this_matters_prompt(
        primary_concern,
        primary_mode.trigger_conditions,
        primary_mode.why_subtle
    )
    
    try:
        return call_llm(prompt)
    except Exception:
        return None

def build_report(
    failure_modes, 
    assumptions, 
    parsed_doc: ParsedDocument,
    parsed_doc_text: str = "",
    pattern_library: FailurePatternLibrary = None,
    contextual_metadata: dict = None
):
    # Sort failure modes by confidence and match strength (high first) for ranking
    sorted_modes = sorted(
        failure_modes,
        key=lambda m: (
            m.confidence == ConfidenceLevel.high,
            m.match_strength or 0,
            m.confidence == ConfidenceLevel.medium
        ),
        reverse=True
    )
    
    overall_risk = (
        ConfidenceLevel.high if any(m.confidence == ConfidenceLevel.high for m in failure_modes)
        else ConfidenceLevel.medium if failure_modes
        else ConfidenceLevel.low
    )
    primary = sorted_modes[0].name if sorted_modes else None
    
    # Generate "why this matters" explanation
    why_matters = generate_why_this_matters(primary, sorted_modes)
    
    # Determine ruled-out risks dynamically
    ruled_out = determine_ruled_out_risks(parsed_doc_text, sorted_modes)
    
    # Detect unknowns
    unknowns = []
    if pattern_library:
        unknowns = detect_unknowns(parsed_doc, sorted_modes, pattern_library, contextual_metadata)
    
    # Get version information
    version_info = get_version_info()

    # Generate summary if we have failure modes
    summary_text = "See failure modes below."
    if sorted_modes:
        from app.synthesis import synthesize_summary
        try:
            summary_text = synthesize_summary(sorted_modes)
        except Exception:
            # Fallback to default
            pass
    
    # Extract document section headings for reference
    document_sections = [section.heading for section in parsed_doc.sections] if parsed_doc else None
    
    return SecondOpinionReport(
        overall_risk=overall_risk,
        primary_concern=primary,
        why_this_matters=why_matters,
        summary=summary_text,
        failure_modes=sorted_modes,
        assumptions=assumptions,
        ruled_out=ruled_out,
        unknowns=unknowns,
        version_info=version_info,
        document_sections=document_sections
    )
