"""
Basic Tests for Second Opinion
"""
import pytest
from app.models import FailurePattern, Finding, ConfidenceLevel, PatternCategory
from app.patterns import get_all_patterns, get_pattern_by_id


def test_patterns_loaded():
    """Test that all patterns are loaded"""
    patterns = get_all_patterns()
    assert len(patterns) == 16
    assert all(isinstance(p, FailurePattern) for p in patterns)


def test_pattern_structure():
    """Test pattern data structure"""
    pattern = get_all_patterns()[0]
    assert pattern.id
    assert pattern.name
    assert pattern.description
    assert pattern.category in PatternCategory


def test_get_pattern_by_id():
    """Test retrieving pattern by ID"""
    pattern = get_pattern_by_id("thundering_herd")
    assert pattern is not None
    assert pattern.name == "Thundering Herd Amplification"

    # Test non-existent pattern
    assert get_pattern_by_id("nonexistent") is None


def test_finding_model():
    """Test Finding data model"""
    finding = Finding(
        pattern_id="test_id",
        pattern_name="Test Pattern",
        confidence=ConfidenceLevel.HIGH,
        match_score=0.85,
        evidence=["Evidence 1", "Evidence 2"],
        trigger_conditions=["Condition 1"],
        why_easy_to_miss="Explanation",
        discussion_questions=["Question 1"]
    )

    assert finding.confidence == ConfidenceLevel.HIGH
    assert finding.match_score == 0.85
    assert len(finding.evidence) == 2


def test_confidence_levels():
    """Test confidence level enum"""
    assert ConfidenceLevel.HIGH.value == "high"
    assert ConfidenceLevel.MEDIUM.value == "medium"
    assert ConfidenceLevel.LOW.value == "low"


def test_pattern_categories():
    """Test pattern categories"""
    categories = {p.category for p in get_all_patterns()}
    expected = {
        PatternCategory.LOAD,
        PatternCategory.DEPENDENCY,
        PatternCategory.DATA,
        PatternCategory.TIMING,
        PatternCategory.RESOURCE,
        PatternCategory.DISTRIBUTED
    }
    assert categories == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])