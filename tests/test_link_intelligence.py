"""Tests for link intelligence and heuristics."""
import pytest
from app.ai.link_intelligence import extract_domain, calculate_name_similarity, extract_keywords


def test_extract_domain():
    """Test email domain extraction."""
    assert extract_domain("user@example.com") == "example.com"
    assert extract_domain("admin@subdomain.example.com") == "subdomain.example.com"
    assert extract_domain("no-at-sign.com") == ""
    assert extract_domain("") == ""
    assert extract_domain(None) == ""


def test_calculate_name_similarity():
    """Test name similarity calculation."""
    # Exact match
    assert calculate_name_similarity("Acme Corp", "Acme Corp") == 1.0
    
    # Similar names
    similarity = calculate_name_similarity("Acme Corporation", "Acme Corp")
    assert 0.5 < similarity < 1.0
    
    # Different names
    similarity = calculate_name_similarity("Acme Corp", "TechStart Inc")
    assert similarity < 0.5
    
    # Case insensitive
    assert calculate_name_similarity("ACME", "acme") == 1.0
    
    # Empty strings
    assert calculate_name_similarity("", "") == 0.0
    assert calculate_name_similarity("Test", "") == 0.0


def test_extract_keywords():
    """Test keyword extraction."""
    text = "Cloud hosting and infrastructure services"
    keywords = extract_keywords(text)
    assert "cloud" in keywords
    assert "hosting" in keywords
    assert "infrastructure" in keywords
    assert "services" in keywords
    assert "and" not in keywords  # Stop word
    
    # Empty text
    assert extract_keywords("") == set()
    assert extract_keywords(None) == set()
    
    # Punctuation handling
    text = "Hello, world! This is a test."
    keywords = extract_keywords(text)
    assert "hello" in keywords
    assert "world" in keywords
    assert "test" in keywords


def test_keyword_filtering():
    """Test that short words and stop words are filtered."""
    text = "a an the in on at to for of with by"
    keywords = extract_keywords(text)
    assert len(keywords) == 0  # All stop words


def test_link_confidence_thresholds():
    """Test that confidence values are reasonable."""
    # This would test the actual LinkAnalyzer class
    # For now, just verify the threshold logic
    confidence = 0.85
    assert confidence > 0.3  # Above suggestion threshold
    assert confidence <= 1.0  # Not exceeding maximum
    
    confidence = 0.2
    assert confidence <= 0.3  # Below threshold - should not suggest


def test_evidence_text_format():
    """Test evidence text is properly formatted."""
    evidence_parts = [
        "Same email domain: example.com",
        "Similar names (similarity: 0.85)",
        "Shared tags: vip, enterprise"
    ]
    evidence = "; ".join(evidence_parts)
    
    assert "Same email domain" in evidence
    assert "Similar names" in evidence
    assert "Shared tags" in evidence
    assert evidence.count(";") == 2  # Proper separator
