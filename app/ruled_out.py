from app.llm import call_llm
from app.prompts import get_ruled_out_risks_prompt
from typing import List

# Common risks that might be ruled out if not relevant to the design
COMMON_RISKS = [
    "Network saturation",
    "Memory pressure",
    "Cross-region latency",
    "CPU exhaustion",
    "Disk I/O bottlenecks",
    "Database connection pool exhaustion",
    "SSL/TLS handshake failures",
    "DNS resolution failures",
    "Load balancer failures",
    "Container orchestration failures"
]

def determine_ruled_out_risks(parsed_doc_text: str, matched_patterns: List) -> List[str]:
    """
    Determine which common risks should be ruled out based on the design.
    Uses LLM to analyze if risks are not relevant to the current design.
    """
    if not parsed_doc_text:
        return []
    
    # Get pattern names that were matched
    matched_pattern_names = [p.name for p in matched_patterns] if matched_patterns else []
    
    # Limit to avoid token issues
    doc_snippet = parsed_doc_text[:2000]
    
    prompt = get_ruled_out_risks_prompt(doc_snippet, matched_pattern_names, COMMON_RISKS)
    
    try:
        response = call_llm(prompt)
        # Parse the response
        if not response or "none" in response.lower() or "empty" in response.lower():
            return []
        
        # Extract risk names from response
        ruled_out = []
        for risk in COMMON_RISKS:
            if risk.lower() in response.lower():
                ruled_out.append(risk)
        
        return ruled_out[:5]  # Limit to 5
    except Exception:
        # Fallback to empty list on error
        return []
