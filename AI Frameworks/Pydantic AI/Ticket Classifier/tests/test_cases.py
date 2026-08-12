# tests/test_cases.py

import pytest
from fastapi.testclient import TestClient
from pydantic_ai.models.test import TestModel
from app.api import app
from app.agent import agent
from app.database import init_db, get_db_connection

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Initializes the database schema and clears tables before each test."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tickets")
    conn.commit()
    conn.close()
    
    init_db()

def test_health_endpoint():
    """Tests the health check endpoint returns 200 and details."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data

def test_classify_ticket_api():
    """Tests the classification API endpoint with a mocked agent model."""
    test_model = TestModel()
    
    with agent.override(model=test_model):
        response = client.post(
            "/api/v1/tickets/classify",
            json={"message": "I was charged twice on my card."}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None
        assert data["ticket_message"] == "I was charged twice on my card."
        assert data["category"] == "billing"
        assert data["priority"] == "low"
        assert data["suggested_agent"] == "billing_agent"
        assert data["confidence"] == 0.0
        assert data["summary"] == "a"
        assert data["requires_human_review"] is False

def test_get_tickets_api():
    """Tests fetching tickets from the history endpoint."""
    # Add a mock ticket first using the classification endpoint
    test_model = TestModel()
    
    with agent.override(model=test_model):
        client.post(
            "/api/v1/tickets/classify",
            json={"message": "What are your support hours?"}
        )
        
    response = client.get("/api/v1/tickets")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["ticket_message"] == "What are your support hours?"
    assert tickets[0]["category"] == "billing"

def test_get_metrics_api():
    """Tests that metrics aggregate classifications correctly."""
    # Verify starting metrics
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_tickets"] == 0
    
    # Classify a ticket to add to metrics
    test_model = TestModel()
    
    with agent.override(model=test_model):
        client.post(
            "/api/v1/tickets/classify",
            json={"message": "Someone changed my login email address."}
        )
        
    # Get updated metrics
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_tickets"] == 1
    assert metrics["category_distribution"]["billing"] == 1
    assert metrics["priority_distribution"]["low"] == 1
    assert metrics["requires_human_review_rate"] == 0.0
    assert metrics["average_confidence"] == 0.0

def test_reclassify_ticket_api():
    """Tests reclassifying an existing ticket via the API."""
    # First add a ticket
    test_model = TestModel()
    with agent.override(model=test_model):
        resp = client.post(
            "/api/v1/tickets/classify",
            json={"message": "Card charged twice."}
        )
    ticket_id = resp.json()["id"]
    
    # Reclassify
    reclass_resp = client.post(
        f"/api/v1/tickets/{ticket_id}/reclassify",
        json={
            "category": "refund",
            "priority": "high",
            "suggested_agent": "billing_agent"
        }
    )
    assert reclass_resp.status_code == 200
    assert reclass_resp.json()["status"] == "success"
    
    # Verify DB update
    get_resp = client.get("/api/v1/tickets")
    tickets = get_resp.json()
    assert tickets[0]["category"] == "refund"
    assert tickets[0]["priority"] == "high"
    assert tickets[0]["suggested_agent"] == "billing_agent"
    assert tickets[0]["is_reclassified"] is True
