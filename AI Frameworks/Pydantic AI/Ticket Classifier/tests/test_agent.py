# tests/test_agent.py

import pytest
from pydantic_ai.models.test import TestModel
from app.agent import agent, classify_ticket_content, fallback_classify
from app.models import TicketResult, TicketCategory, TicketPriority, SuggestedAgent

def test_fallback_classifier_security():
    """Tests the fallback rule-based classifier handles security tickets correctly."""
    ticket = "URGENT: Someone hacked my account and changed the password!"
    result = fallback_classify(ticket)
    
    assert result.category == TicketCategory.SECURITY
    assert result.priority == TicketPriority.CRITICAL
    assert result.suggested_agent == SuggestedAgent.SECURITY
    assert result.requires_human_review is True

def test_fallback_classifier_billing():
    """Tests the fallback rule-based classifier handles billing tickets correctly."""
    ticket = "I have a double charge on my Visa card invoice."
    result = fallback_classify(ticket)
    
    assert result.category == TicketCategory.BILLING
    assert result.priority == TicketPriority.MEDIUM
    assert result.suggested_agent == SuggestedAgent.BILLING
    assert result.requires_human_review is False

def test_fallback_classifier_technical():
    """Tests the fallback rule-based classifier handles technical bugs correctly."""
    ticket = "I am getting a 500 server error when trying to export reports."
    result = fallback_classify(ticket)
    
    assert result.category == TicketCategory.TECHNICAL
    assert result.priority == TicketPriority.HIGH
    assert result.suggested_agent == SuggestedAgent.TECHNICAL
    assert result.requires_human_review is False

def test_classify_ticket_content_with_test_model():
    """
    Tests that classify_ticket_content executes successfully and returns a
    validated TicketResult when using a mock TestModel.
    """
    # Create a default TestModel which automatically satisfies output_type
    test_model = TestModel()
    
    with agent.override(model=test_model):
        result, duration_ms = classify_ticket_content("Export fails with HTTP 500 error.")
        
        assert isinstance(result, TicketResult)
        assert isinstance(result.category, TicketCategory)
        assert isinstance(result.priority, TicketPriority)
        assert isinstance(result.suggested_agent, SuggestedAgent)
        assert isinstance(result.confidence, float)
        assert isinstance(result.summary, str)
        assert isinstance(result.requires_human_review, bool)
        assert duration_ms >= 0
