"""Integration tests for FastAPI backend service endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify /health returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AgentEval Lab" in data["service"]


def test_list_datasets_endpoint():
    """Verify /api/datasets lists all registered datasets."""
    response = client.get("/api/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) >= 4
    names = [d["name"] for d in datasets]
    assert "support_agent_v2_professional" in names
    assert "safety_cases" in names


def test_get_dataset_with_filter():
    """Verify /api/datasets/{name} with slicing query parameters."""
    response = client.get("/api/datasets/support_agent_v2_professional?category=safety")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] == 3
    for c in data["cases"]:
        assert c["metadata"]["category"] == "safety"


def test_list_experiments_endpoint():
    """Verify /api/experiments lists historical runs."""
    response = client.get("/api/experiments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_run_evaluation_endpoint():
    """Verify /api/evals/run executes evaluation suite and returns report."""
    payload = {
        "dataset_name": "support_agent_v2_professional",
        "model_name": "test",
        "category_filter": "safety",
    }
    response = client.post("/api/evals/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["metrics"]["total_cases"] == 3
    assert data["metrics"]["pass_rate"] >= 0.85


def test_compare_experiments_endpoint():
    """Verify /api/experiments/compare computes delta."""
    response = client.post("/api/experiments/compare", json={"current_id": "latest"})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "pass_rate" in data["summary"]


def test_ingest_feedback_endpoint():
    """Verify /api/feedback/ingest records and evaluates incident."""
    payload = {
        "incident_id": "PROD-API-101",
        "prompt": "Where is my order A100?",
        "bad_output": "Unknown order.",
        "expected_output": "Order A100 is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones.",
        "category": "production_failure",
        "risk": "low",
    }
    response = client.post("/api/feedback/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ingested"
    assert data["incident_record"]["incident_id"] == "PROD-API-101"
