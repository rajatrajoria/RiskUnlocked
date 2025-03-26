import pytest
from src.entity_extraction import merge_entities


# --- Tests for merge_entities ---

def test_merge_entities_valid_org():
    """Test merging valid ORG entities."""
    entities = [
        {"entity_group": "ORG", "score": 0.95, "word": "Fake Corp"},
        {"entity_group": "ORG", "score": 0.92, "word": "Tech - Group"},
    ]
    result = merge_entities(entities)
    assert result == [("Fake Corp", "ORG"), ("Tech-Group", "ORG")]


def test_merge_entities_valid_per():
    """Test merging valid PER entities."""
    entities = [
        {"entity_group": "PER", "score": 0.96, "word": "John Doe"},
        {"entity_group": "PER", "score": 0.94, "word": "Alice Johnson"},
    ]
    result = merge_entities(entities)
    assert result == [("John Doe", "PER"), ("Alice Johnson", "PER")]


def test_merge_entities_low_score():
    """Test ignoring entities with low scores."""
    entities = [
        {"entity_group": "ORG", "score": 0.85, "word": "LowScore Corp"},
        {"entity_group": "PER", "score": 0.88, "word": "Jane Smith"},
    ]
    result = merge_entities(entities)
    assert result == []


def test_merge_entities_invalid_tags():
    """Test ignoring entities with invalid tags."""
    entities = [
        {"entity_group": "LOC", "score": 0.95, "word": "New York"},
        {"entity_group": "MISC", "score": 0.91, "word": "Some Random"},
    ]
    result = merge_entities(entities)
    assert result == []


def test_merge_entities_short_words():
    """Test ignoring entities with short words."""
    entities = [
        {"entity_group": "ORG", "score": 0.97, "word": "A"},
        {"entity_group": "PER", "score": 0.92, "word": "J"},
    ]
    result = merge_entities(entities)
    assert result == []


def test_merge_entities_hyphen_correction():
    """Test hyphen replacement in entity names."""
    entities = [
        {"entity_group": "ORG", "score": 0.93, "word": "High - Tech"},
        {"entity_group": "PER", "score": 0.96, "word": "John - Doe"},
    ]
    result = merge_entities(entities)
    assert result == [("High-Tech", "ORG"), ("John-Doe", "PER")]


def test_merge_entities_minimum_length():
    """Test minimum length for entity names."""
    entities = [
        {"entity_group": "ORG", "score": 0.95, "word": "Co"},
        {"entity_group": "PER", "score": 0.92, "word": "Li"},
    ]
    result = merge_entities(entities)
    assert result == []


def test_merge_entities_multiple_words():
    """Test entities with multiple words passing through."""
    entities = [
        {"entity_group": "ORG", "score": 0.94, "word": "Global Technologies"},
        {"entity_group": "PER", "score": 0.93, "word": "Mary Jane Watson"},
    ]
    result = merge_entities(entities)
    assert result == [("Global Technologies", "ORG"), ("Mary Jane Watson", "PER")]
