"""
Prompt Library for Second Opinion

Centralized location for all LLM prompts used in the system.
This enables versioning, consistency, and easier maintenance.
"""


def sanitize_for_prompt(text: str) -> str:
    """Sanitize user input to prevent prompt injection.
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
    """
    # Remove potential prompt injection patterns
    text = text.replace("```", "")
    text = text.replace("Ignore previous instructions", "")
    text = text.replace("Ignore all previous", "")
    # Limit length to prevent token issues
    return text[:1000]

# System Prompt
SYSTEM_PROMPT = """You are a Senior Staff Engineer. Review this RFC, design document, or PR description for architectural bottlenecks, security risks, and scalability concerns. Be concise and critical."""


# Assumption Extraction Prompt
def get_assumption_extraction_prompt(section_heading: str, section_content: str) -> str:
    """
    Generate prompt for extracting implicit assumptions from a design section.
    
    Args:
        section_heading: The heading of the section
        section_content: The content of the section (will be truncated to 1000 chars)
    """
    # Sanitize and limit content to prevent prompt injection
    content_snippet = sanitize_for_prompt(section_content)
    
    return f"""Extract implicit assumptions from this design section.
Focus on:
- Modal language ("expected to", "should", "unlikely")
- Stability claims without enforcement ("latency remains low", "dependency stays stable")
- Invariant claims ("traffic is predictable", "load is consistent")

Only list assumptions that are clearly implied. Do not speculate or infer.

Section: {section_heading}
Content:
{content_snippet}

Return only the assumptions, one per line. If no clear assumptions, return "None"."""


# Synthesis Summary Prompt
def get_synthesis_summary_prompt(failure_modes_detail: list[str]) -> str:
    """
    Generate prompt for synthesizing a conservative summary of architectural risks.
    
    Args:
        failure_modes_detail: List of formatted failure mode descriptions
    """
    modes_text = "\n".join(failure_modes_detail)
    
    return f"""You are a calm, experienced staff engineer reviewing an RFC, design document, or PR description.

The following failure modes were identified:
{modes_text}

Generate a brief, conservative summary (2-3 sentences) of the overall architectural risk posture.
- Use plain, non-alarmist language
- Focus on why these patterns matter in production
- Do not prescribe fixes or solutions
- Be thoughtful and measured

Summary:"""


# Ruled Out Risks Prompt
def get_ruled_out_risks_prompt(
    doc_snippet: str,
    matched_pattern_names: list[str],
    common_risks: list[str]
) -> str:
    """
    Generate prompt for determining which common risks should be ruled out.
    
    Args:
        doc_snippet: Snippet of the design document (typically first 2000 chars)
        matched_pattern_names: List of matched failure pattern names
        common_risks: List of common risks to consider
    """
    patterns_text = ', '.join(matched_pattern_names) if matched_pattern_names else 'None'
    risks_text = ', '.join(common_risks)
    
    return f"""You are analyzing a distributed systems RFC, design document, or PR description.

Design content:
{doc_snippet}

Matched failure patterns:
{patterns_text}

Common risks to consider:
{risks_text}

Based on the design, which of these common risks are clearly NOT applicable or already addressed?
Return ONLY a comma-separated list of risk names (max 5). If none are clearly ruled out, return an empty list.
Be conservative - only rule out risks that are clearly not relevant.

Example format: "Network saturation, Memory pressure"
"""


# Why This Matters Prompt
def get_why_this_matters_prompt(
    failure_mode_name: str,
    trigger_conditions: list[str],
    why_subtle: list[str]
) -> str:
    """
    Generate prompt for explaining why a failure mode matters.
    
    Args:
        failure_mode_name: Name of the failure mode
        trigger_conditions: List of trigger conditions
        why_subtle: List of reasons why it's subtle
    """
    triggers_text = ', '.join(trigger_conditions[:3])
    subtle_text = ', '.join(why_subtle[:2])
    
    return f"""Explain why this failure mode matters in plain language. Be concise (2-3 sentences).

Failure Mode: {failure_mode_name}
Trigger Conditions: {triggers_text}
Why It's Subtle: {subtle_text}

Focus on why this is a real concern that could surface in production, not just a theoretical risk.
"""


# Pattern Matcher Semantic Prompt (for alternative pattern matching approach)
def get_pattern_matcher_prompt(design_text: str, matches: list[dict]) -> str:
    """
    Generate prompt for semantic pattern matching.
    
    Args:
        design_text: The full design document text
        matches: List of matched patterns with their details
    """
    patterns_text = ""
    for m in matches:
        triggers = ', '.join(m.get('trigger_conditions', []))
        patterns_text += f"- {m['name']}: {triggers}\n"
    
    return f"""You are a senior distributed systems engineer.
Analyze the following RFC, design document, or PR description for subtle failure modes:

{design_text}

Relevant failure patterns:
{patterns_text}

Generate a structured pre-mortem review with:
1. Overview / Overall Risk
2. Potential Failure Modes (ranked)
3. Assumptions Detected
4. Questions for the team
"""
