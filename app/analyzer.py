"""
Design Analyzer
Core analysis engine for detecting failure patterns in design documents
"""
import asyncio
import difflib
from typing import Awaitable, Callable, Dict, List, Optional

from app.config import settings
from app.llm import llm_client
from app.models import ConfidenceLevel, Finding
from app.patterns import get_all_patterns

ProgressCallback = Callable[[str, Optional[dict]], Awaitable[None]]


class DesignAnalyzer:
    """Main analyzer for design documents"""

    def __init__(self):
        self.patterns = get_all_patterns()
        self.llm = llm_client
        self._pattern_names = [p.name for p in self.patterns]

    async def analyze(
        self,
        document: str,
        context: Optional[Dict] = None,
        on_progress: Optional[ProgressCallback] = None,
    ) -> Dict:
        if len(document) > settings.max_document_size:
            raise ValueError(f"Document too large. Max size: {settings.max_document_size} characters")

        context = context or {}

        async def progress(step: str, data: Optional[dict] = None):
            if on_progress:
                await on_progress(step, data)

        await progress("start")

        # Round 1: pattern matching, assumptions, and unknowns run in parallel
        findings, assumptions, unknowns = await asyncio.gather(
            self._match_patterns(document, context),
            self._extract_assumptions(document, context),
            self._find_known_unknowns(document, context),
        )

        await progress("patterns_done", {"count": len(findings)})

        # Round 2: ruled-out depends on findings from round 1
        ruled_out = await self._identify_ruled_out_risks(document, findings)

        await progress("analysis_done")

        summary = self._generate_summary(findings, assumptions)

        await progress("complete")

        return {
            "failure_modes": [self._finding_to_dict(f) for f in findings],
            "implicit_assumptions": assumptions,
            "ruled_out_risks": ruled_out,
            "known_unknowns": unknowns,
            "summary": summary,
        }

    def _resolve_pattern(self, name: str):
        """Find the best matching pattern — exact first, then fuzzy fallback."""
        pattern = next((p for p in self.patterns if p.name.lower() == name.lower()), None)
        if pattern:
            return pattern
        close = difflib.get_close_matches(name, self._pattern_names, n=1, cutoff=0.6)
        if close:
            return next((p for p in self.patterns if p.name == close[0]), None)
        return None

    async def _match_patterns(self, document: str, context: Dict) -> List[Finding]:
        """Match document against failure patterns"""
        pattern_descriptions = "\n".join([
            f"{i+1}. {p.name}: {p.description}\n   Key signals: {', '.join(p.indicators)}"
            for i, p in enumerate(self.patterns)
        ])

        system_prompt = """You are an expert in distributed systems and failure analysis.
Your task is to identify potential failure modes in system design documents.
Be conservative - only report patterns with clear evidence.
Focus on what could go wrong, not what's already addressed."""

        prompt = f"""Analyze this design document for potential failure patterns.

DESIGN DOCUMENT:
{document}

{f"CONTEXT: {context}" if context else ""}

FAILURE PATTERNS TO CHECK:
{pattern_descriptions}

For each pattern that matches, provide:
1. Pattern name (exact match from list above)
2. Confidence (high/medium/low)
3. Evidence (specific quotes or references from document)
4. Trigger conditions (what would cause this failure)
5. Why it's easy to miss
6. Discussion questions for the team

Respond in JSON format:
{{
  "matches": [
    {{
      "pattern_name": "...",
      "confidence": "high|medium|low",
      "match_score": 0.85,
      "evidence": ["quote 1", "quote 2"],
      "trigger_conditions": ["condition 1", "condition 2"],
      "why_easy_to_miss": "explanation",
      "discussion_questions": ["question 1", "question 2"]
    }}
  ]
}}

Only include patterns with clear evidence. Return empty matches array if no patterns found."""

        try:
            result = await self.llm.generate_json(prompt, system_prompt)
            matches = result.get("matches", [])

            findings = []
            for match in matches[: settings.max_failure_modes]:
                pattern = self._resolve_pattern(match.get("pattern_name", ""))

                if pattern and match.get("match_score", 0) >= settings.confidence_threshold:
                    finding = Finding(
                        pattern_id=pattern.id,
                        pattern_name=pattern.name,
                        confidence=ConfidenceLevel(match["confidence"]),
                        match_score=match["match_score"],
                        evidence=match.get("evidence", []),
                        trigger_conditions=match.get("trigger_conditions", []),
                        why_easy_to_miss=match.get("why_easy_to_miss", pattern.why_easy_to_miss),
                        discussion_questions=match.get("discussion_questions", []),
                    )
                    findings.append(finding)

            findings.sort(
                key=lambda f: ({"high": 3, "medium": 2, "low": 1}[f.confidence], f.match_score),
                reverse=True,
            )
            return findings

        except Exception as e:
            print(f"Pattern matching error: {e}")
            return []

    async def _extract_assumptions(self, document: str, context: Dict) -> List[str]:
        """Extract implicit assumptions from document"""
        prompt = f"""Analyze this design document and identify implicit assumptions.
Look for unstated expectations about:
- System behavior under load
- Network reliability
- Data consistency
- Timing and ordering
- Resource availability
- Third-party services

DOCUMENT:
{document}

List 3-5 key implicit assumptions. Be specific and evidence-based.
Respond as JSON: {{"assumptions": ["assumption 1", "assumption 2", ...]}}"""

        try:
            result = await self.llm.generate_json(prompt)
            return result.get("assumptions", [])[:5]
        except Exception as e:
            print(f"Assumption extraction error: {e}")
            return []

    async def _identify_ruled_out_risks(self, document: str, findings: List[Finding]) -> List[str]:
        """Identify risks that are explicitly ruled out"""
        found_patterns = {f.pattern_name for f in findings}
        not_found = [p.name for p in self.patterns if p.name not in found_patterns]

        if not not_found:
            return []

        prompt = f"""Based on this document, which of these failure patterns are explicitly NOT applicable?

DOCUMENT:
{document}

PATTERNS TO CHECK:
{chr(10).join(f"- {p}" for p in not_found[:10])}

Only include patterns that are clearly ruled out by explicit design choices.
Respond as JSON: {{"ruled_out": ["pattern 1", "pattern 2", ...]}}"""

        try:
            result = await self.llm.generate_json(prompt)
            return result.get("ruled_out", [])[:5]
        except Exception as e:
            print(f"Ruled-out risks error: {e}")
            return []

    async def _find_known_unknowns(self, document: str, context: Dict) -> List[str]:
        """Identify areas where critical information is missing"""
        prompt = f"""Identify critical information gaps in this design document.
Look for:
- Missing performance requirements
- Unspecified failure handling
- Unclear scaling strategy
- Missing monitoring/observability
- Undefined SLOs or SLAs

DOCUMENT:
{document}

List 3-5 critical known unknowns. Be specific about what's missing and why it matters.
Respond as JSON: {{"unknowns": ["unknown 1", "unknown 2", ...]}}"""

        try:
            result = await self.llm.generate_json(prompt)
            return result.get("unknowns", [])[:5]
        except Exception as e:
            print(f"Known unknowns error: {e}")
            return []

    def _generate_summary(self, findings: List[Finding], assumptions: List[str]) -> str:
        """Generate executive summary"""
        if not findings and not assumptions:
            return "No significant failure patterns or concerning assumptions identified. Consider running analysis again with more context."

        high_confidence = [f for f in findings if f.confidence == ConfidenceLevel.HIGH]
        medium_confidence = [f for f in findings if f.confidence == ConfidenceLevel.MEDIUM]

        summary_parts = []

        if high_confidence:
            summary_parts.append(
                f"Found {len(high_confidence)} high-confidence failure pattern(s): "
                f"{', '.join(f.pattern_name for f in high_confidence[:3])}."
            )
        if medium_confidence:
            summary_parts.append(
                f"Identified {len(medium_confidence)} medium-confidence concern(s) worth reviewing."
            )
        if assumptions:
            summary_parts.append(
                f"Detected {len(assumptions)} implicit assumption(s) that should be validated."
            )

        return " ".join(summary_parts)

    def _finding_to_dict(self, finding: Finding) -> Dict:
        """Convert Finding to dictionary"""
        return {
            "pattern_id": finding.pattern_id,
            "pattern_name": finding.pattern_name,
            "confidence": finding.confidence,
            "match_score": finding.match_score,
            "evidence": finding.evidence,
            "trigger_conditions": finding.trigger_conditions,
            "why_easy_to_miss": finding.why_easy_to_miss,
            "discussion_questions": finding.discussion_questions,
        }

    async def check_llm_health(self) -> bool:
        """Check if LLM service is healthy"""
        return await self.llm.check_health()
