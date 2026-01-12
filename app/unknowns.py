"""
Unknowns Detection Engine
Detects areas where required signals are missing or critical dimensions are unspecified.
"""
from typing import List
from app.models import ParsedDocument, FailurePatternMatch
from app.patterns import FailurePatternLibrary

def detect_unknowns(
    parsed_doc: ParsedDocument,
    matched_patterns: List[FailurePatternMatch],
    pattern_library: FailurePatternLibrary,
    contextual_metadata: dict = None
) -> List[str]:
    """
    Detect known unknowns - areas where information is missing or unspecified.
    
    Returns list of unknown areas that could affect failure mode analysis.
    """
    unknowns = []
    
    full_text = " ".join(section.content.lower() for section in parsed_doc.sections)
    
    # 1. Check for missing critical dimensions
    if not contextual_metadata or not contextual_metadata.get("expected_scale_qps"):
        if "scale" not in full_text and "qps" not in full_text and "throughput" not in full_text:
            unknowns.append("Expected scale (QPS/throughput) not specified")
    
    if not contextual_metadata or not contextual_metadata.get("critical_slos_latency"):
        if "slo" not in full_text and "latency" not in full_text.lower() and "p99" not in full_text.lower():
            unknowns.append("Critical SLOs (latency) not specified")
    
    if not contextual_metadata or not contextual_metadata.get("critical_slos_availability"):
        if "availability" not in full_text.lower() and "uptime" not in full_text.lower():
            unknowns.append("Critical SLOs (availability) not specified")
    
    # 2. Check for missing multi-region considerations
    if "region" not in full_text.lower() and "multi-region" not in full_text.lower():
        unknowns.append("Multi-region behavior and failover strategy not specified")
    
    # 3. Check for missing monitoring/observability
    if "monitoring" not in full_text.lower() and "observability" not in full_text.lower() and "metrics" not in full_text.lower():
        unknowns.append("Monitoring and observability strategy not specified")
    
    # 4. Check for missing load testing information
    if "load test" not in full_text.lower() and "stress test" not in full_text.lower() and "chaos" not in full_text.lower():
        unknowns.append("Load testing and failure simulation strategy not specified")
    
    # 5. Check for patterns that might be relevant but signals are missing
    # Look for patterns that could apply but don't have matching signals
    all_patterns = pattern_library.all()
    matched_pattern_ids = {p.pattern_id for p in matched_patterns}
    
    # Check for patterns with required_context that's missing from document
    for pattern in all_patterns:
        if pattern["id"] not in matched_pattern_ids:
            required_context = pattern.get("required_context", [])
            if required_context:
                # Check if document mentions any of the required context fields
                missing_context = []
                for context_field in required_context:
                    # Check if context field is mentioned in document
                    context_lower = context_field.lower().replace("_", " ")
                    if context_lower not in full_text and context_field.lower() not in full_text:
                        missing_context.append(context_field)
                
                # If significant context is missing, add to unknowns
                if len(missing_context) == len(required_context):
                    # All required context is missing
                    unknowns.append(f"Pattern '{pattern['name']}' may be relevant but required context missing: {', '.join(required_context[:3])}")
    
    # Check for common missing patterns that might be relevant
    potential_missing_patterns = []
    for pattern in all_patterns:
        if pattern["id"] not in matched_pattern_ids:
            # Check if design mentions related concepts but not the specific signals
            pattern_name_lower = pattern["name"].lower()
            if any(word in full_text for word in pattern_name_lower.split()[:2]):
                # Design mentions pattern-related concepts but pattern didn't match
                potential_missing_patterns.append(pattern["name"])
    
    if potential_missing_patterns:
        unknowns.append(f"Design mentions concepts related to: {', '.join(potential_missing_patterns[:3])}, but insufficient signals detected")
    
    # 6. Check for missing dependency information
    if not contextual_metadata or not contextual_metadata.get("known_dependencies"):
        if "dependency" in full_text.lower() or "service" in full_text.lower():
            if "dependency" not in full_text.lower() or len([s for s in parsed_doc.sections if "dependency" in s.heading.lower()]) == 0:
                unknowns.append("Dependency list and failure modes not explicitly documented")
    
    # 7. Check for missing traffic patterns
    if "traffic" not in full_text.lower() and "request" not in full_text.lower() and "load" not in full_text.lower():
        unknowns.append("Traffic patterns and load characteristics not specified")
    
    # 8. Check for missing error handling
    if "error" not in full_text.lower() and "failure" not in full_text.lower() and "exception" not in full_text.lower():
        unknowns.append("Error handling and failure recovery strategies not explicitly documented")
    
    return unknowns[:10]  # Limit to top 10 unknowns
