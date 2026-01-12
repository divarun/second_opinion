from app.models import Assumption, ConfidenceLevel, ParsedDocument
from app.llm import call_llm
from app.prompts import get_assumption_extraction_prompt
import re

def extract_assumptions(parsed_doc: ParsedDocument) -> list[Assumption]:
    """
    Extract implicit assumptions from RFC, design document, or PR description.
    Targets modal language, stability claims, and invariant claims.
    """
    assumptions = []
    
    # Modal language patterns
    modal_patterns = [
        r'\b(expected to|should|will|likely|unlikely|assumed|assumes)\b',
        r'\b(remains|stays|maintains).*(stable|low|constant|predictable)',
        r'\b(traffic|load|latency|availability).*(is|remains|stays).*(predictable|stable|consistent)'
    ]
    
    for section in parsed_doc.sections:
        section_text = section.content.lower()
        
        # Check for modal language
        has_modal = any(re.search(pattern, section_text, re.IGNORECASE) for pattern in modal_patterns)
        
        if has_modal or len(section.content) > 200:  # Only process substantial sections
            prompt = get_assumption_extraction_prompt(section.heading, section.content)
            
            try:
                response = call_llm(prompt)
                
                # Parse response
                for line in response.splitlines():
                    line = line.strip()
                    # Skip empty lines, "None", or error messages
                    if line and line.lower() != "none" and not line.startswith("Error:"):
                        # Clean up common LLM prefixes
                        line = re.sub(r'^[-•*]\s*', '', line)
                        line = re.sub(r'^\d+\.\s*', '', line)
                        if line and len(line) > 10:  # Filter out very short lines
                            assumptions.append(
                                Assumption(
                                    text=line,
                                    source_section=section.heading,
                                    confidence=ConfidenceLevel.medium
                                )
                            )
            except Exception:
                # Graceful failure - continue with other sections
                continue
    
    return assumptions