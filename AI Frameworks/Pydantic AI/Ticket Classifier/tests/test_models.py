# tests/test_models.py

import pytest
from pydantic import ValidationError
from app.models import TicketResult, TicketCategory, TicketPriority, SuggestedAgent

def test_valid_ticket_result():
    """Verifies that a correctly formatted dictionary is validated into a TicketResult model."""
    data = {
        "category": "technical",
        "priority": "high",
        "suggested_agent": "technical_agent",
        "confidence": 0.95,
        "summary": "Database connection failed with error 500.",
        "reasoning": "Connection timed out repeatedly.",
        "requires_human_review": False
    }
    
    result = TicketResult(**data)
    assert result.category == TicketCategory.TECHNICAL
    assert result.priority == TicketPriority.HIGH
    assert result.suggested_agent == SuggestedAgent.TECHNICAL
    assert result.confidence == 0.95
    assert result.requires_human_review is False

def test_invalid_category():
    """Ensures validation fails if category is not a valid enum value."""
    with pytest.raises(ValidationError) as exc_info:
        TicketResult(
            category="invalid_category",
            priority="high",
            suggested_agent="technical_agent",
            confidence=0.95,
            summary="Invalid category test.",
            reasoning="Testing enum boundaries.",
            requires_human_review=False
        )
    assert "Input should be" in str(exc_info.value)

def test_invalid_priority():
    """Ensures validation fails if priority is not a valid enum value."""
    with pytest.raises(ValidationError) as exc_info:
        TicketResult(
            category="technical",
            priority="super_urgent",
            suggested_agent="technical_agent",
            confidence=0.95,
            summary="Invalid priority test.",
            reasoning="Testing enum boundaries.",
            requires_human_review=False
        )
    assert "Input should be" in str(exc_info.value)

def test_out_of_bounds_confidence():
    """Ensures validation fails if confidence score is out of [0.0, 1.0] range."""
    # Test above 1.0
    with pytest.raises(ValidationError):
        TicketResult(
            category="technical",
            priority="high",
            suggested_agent="technical_agent",
            confidence=1.5,
            summary="High confidence error.",
            reasoning="Should fail ge/le bounds.",
            requires_human_review=False
        )
        
    # Test below 0.0
    with pytest.raises(ValidationError):
        TicketResult(
            category="technical",
            priority="high",
            suggested_agent="technical_agent",
            confidence=-0.1,
            summary="Low confidence error.",
            reasoning="Should fail ge/le bounds.",
            requires_human_review=False
        )
