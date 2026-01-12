from app.llm import call_llm
from app.models import FailurePatternMatch
from app.prompts import get_synthesis_summary_prompt
from typing import List

def synthesize_summary(failure_modes: List[FailurePatternMatch]) -> str:
    """
    Generate a conservative summary of architectural risks.
    Aligned with PRD: calm, non-alarmist, plain language.
    """
    if not failure_modes:
        return "No significant failure patterns detected based on the provided RFC, design document, or PR description."

    # Build detailed context for summary
    modes_detail = []
    for m in failure_modes[:3]:  # Focus on top 3
        modes_detail.append(
            f"{m.name} ({m.confidence} confidence): "
            f"Triggered by {', '.join(m.trigger_conditions[:2])}"
        )
    
    prompt = get_synthesis_summary_prompt(modes_detail)
    
    try:
        summary = call_llm(prompt)
        # Fallback if LLM fails
        if not summary or "Error:" in summary:
            primary = failure_modes[0].name if failure_modes else "failure patterns"
            return f"This design shows potential for {primary.lower()}, which typically surface only under real production load or partial outages."
        return summary
    except Exception:
        # Graceful fallback
        primary = failure_modes[0].name if failure_modes else "failure patterns"
        return f"This design shows potential for {primary.lower()}, which typically surface only under real production load or partial outages."