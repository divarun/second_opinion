from app.models import FailurePatternMatch, ConfidenceLevel
import re

def derive_impact_surface(pattern: dict) -> list:
    """Derive impact surface from pattern metadata when not explicitly provided."""
    impact_surface = []
    pattern_name = pattern["name"].lower()
    
    # Common impact surfaces based on pattern characteristics
    if "latency" in pattern_name or "tail" in pattern_name:
        impact_surface.append("User-facing latency spikes")
    if "retry" in pattern_name or "amplification" in pattern_name:
        impact_surface.append("Downstream error amplification")
        impact_surface.append("Increased load on dependencies")
    if "queue" in pattern_name or "backpressure" in pattern_name:
        impact_surface.append("Consumer lag and memory pressure")
    if "cache" in pattern_name or "stampede" in pattern_name:
        impact_surface.append("Backend overload from cache misses")
    if "consistency" in pattern_name or "drift" in pattern_name:
        impact_surface.append("Data inconsistency and user confusion")
    if "partition" in pattern_name or "network" in pattern_name:
        impact_surface.append("Service unavailability in affected regions")
    
    # Default if nothing matches
    if not impact_surface:
        impact_surface.append("Service degradation under failure conditions")
        impact_surface.append("Potential user-facing errors")
    
    return impact_surface

def match_patterns(parsed_doc, pattern_library, assumptions=None):
    """
    Match failure patterns against document content.
    Enhanced scoring with assumption reinforcement and mitigation detection.
    Only returns patterns that have at least one matching signal.
    """
    matches = []
    assumptions = assumptions or []

    full_text = " ".join(
        section.content.lower() for section in parsed_doc.sections
    )
    
    # If document is empty or too short, return no matches
    if not full_text or len(full_text.strip()) < 10:
        return matches

    for pattern in pattern_library.all():
        evidence = []
        score = 0
        assumption_bonus = 0
        mitigation_penalty = 0

        # Primary scoring: signal matching with section-level tracking and context extraction
        for signal in pattern["signals"]:
            signal_lower = signal.lower()
            pattern_re = r'\b' + re.escape(signal_lower) + r'\b'
            
            # Check each section individually to track where signals appear and extract context
            matching_sections = []
            context_snippets = []
            
            for section in parsed_doc.sections:
                # Use original content for matching to preserve case in context
                section_lower = section.content.lower()
                matches = list(re.finditer(pattern_re, section_lower))
                if matches:
                    matching_sections.append(section.heading)
                    # Extract context around first match in this section
                    first_match = matches[0]
                    start_pos = max(0, first_match.start() - 100)
                    end_pos = min(len(section.content), first_match.end() + 100)
                    context = section.content[start_pos:end_pos].strip()
                    
                    # Only add if we successfully extracted context
                    if context:
                        # Clean up context (remove extra whitespace, ensure it's readable)
                        context_cleaned = ' '.join(context.split())
                        # Truncate if too long, but keep it meaningful
                        if len(context_cleaned) > 200:
                            # Find the signal position in the cleaned context (case-insensitive)
                            context_lower = context_cleaned.lower()
                            signal_pos = context_lower.find(signal_lower)
                            if signal_pos >= 0:
                                # Show 80 chars before and after signal
                                before_start = max(0, signal_pos - 80)
                                after_end = min(len(context_cleaned), signal_pos + len(signal) + 80)
                                context_final = context_cleaned[before_start:after_end]
                                if before_start > 0:
                                    context_final = "..." + context_final
                                if after_end < len(context_cleaned):
                                    context_final = context_final + "..."
                                context_snippets.append((section.heading, context_final, signal))
                            else:
                                # Signal not found after cleaning (shouldn't happen, but fallback)
                                context_snippets.append((section.heading, context_cleaned[:200] + "...", signal))
                        else:
                            # Context is short enough, use as-is
                            context_snippets.append((section.heading, context_cleaned, signal))
            
            # Only count signal once, but track all sections where it appears
            if matching_sections:
                score += 1
                # Add evidence with meaningful context
                if context_snippets:
                    # Use the first context snippet as primary evidence
                    section_name, snippet, signal_word = context_snippets[0]
                    if len(matching_sections) == 1:
                        evidence.append(f"Section '{section_name}': \"{snippet}\"")
                    else:
                        evidence.append(f"Section '{section_name}' (and {len(matching_sections)-1} other section{'s' if len(matching_sections) > 2 else ''}): \"{snippet}\"")
                else:
                    # Fallback: if context extraction failed, still add basic evidence
                    if len(matching_sections) == 1:
                        evidence.append(f"Signal '{signal}' found in section: {matching_sections[0]}")
                    else:
                        evidence.append(f"Signal '{signal}' found in sections: {', '.join(matching_sections[:3])}")

        # Only include patterns with at least one matching signal
        if score == 0:
            continue

        # Assumption reinforcement: +Y for reinforcing assumptions
        # Check if assumptions mention pattern-related concepts
        pattern_keywords = [kw.lower() for kw in pattern["name"].split()]
        for assumption in assumptions:
            assumption_lower = assumption.text.lower()
            # If assumption mentions pattern-related concepts, reinforce
            if any(kw in assumption_lower for kw in pattern_keywords[:3]):
                assumption_bonus += 0.5
                evidence.append(f"Reinforced by assumption from section '{assumption.source_section}': {assumption.text[:60]}...")

        # Mitigation detection: -Z for mitigating design elements
        # Use pattern-specific safety_signals if available, otherwise use default list
        safety_signals = pattern.get("safety_signals", [])
        if not safety_signals:
            # Fallback to default mitigation keywords if pattern doesn't have safety_signals
            safety_signals = [
                "circuit breaker", "rate limit", "timeout", "deadline",
                "backpressure", "load shedding", "hedging", "fallback"
            ]
        
        for mitigation in safety_signals:
            # Check which sections mention mitigations (case-insensitive, word boundary matching)
            mitigation_lower = mitigation.lower()
            mitigation_pattern = r'\b' + re.escape(mitigation_lower) + r'\b'
            mitigation_sections = []
            for section in parsed_doc.sections:
                if re.search(mitigation_pattern, section.content.lower()):
                    mitigation_sections.append(section.heading)
            if mitigation_sections:
                mitigation_penalty += 0.3
                if len(mitigation_sections) == 1:
                    evidence.append(f"Mitigation detected in section '{mitigation_sections[0]}': {mitigation}")
                else:
                    evidence.append(f"Mitigation detected in sections {', '.join(mitigation_sections[:2])}: {mitigation}")

        # Calculate final score with bonuses and penalties
        final_score = score + assumption_bonus - mitigation_penalty
        final_score = max(1, final_score)  # Ensure at least 1

        # Assign confidence based on final score
        # High: multiple reinforcing signals (>= 3)
        # Medium: partial match (>= 2 or has assumptions)
        # Low: weak match (== 1, no assumptions)
        if final_score >= 3:
            confidence = ConfidenceLevel.high
        elif final_score >= 2 or assumption_bonus > 0:
            confidence = ConfidenceLevel.medium
        else:
            confidence = ConfidenceLevel.low
        
        # Calculate match strength (0.0 to 1.0) based on final score
        total_signals = len(pattern["signals"])
        match_strength = min(final_score / max(total_signals, 1), 1.0)
        
        # Get impact surface from pattern or derive it
        impact_surface = pattern.get("impact_surface", [])
        if not impact_surface:
            impact_surface = derive_impact_surface(pattern)

        matches.append(
            FailurePatternMatch(
                pattern_id=pattern["id"],
                name=pattern["name"],
                confidence=confidence,
                match_strength=match_strength,
                evidence=evidence,
                trigger_conditions=pattern["trigger_conditions"],
                why_subtle=pattern["why_subtle"],
                impact_surface=impact_surface,
                discussion_questions=pattern["discussion_questions"]
            )
        )

    return matches
