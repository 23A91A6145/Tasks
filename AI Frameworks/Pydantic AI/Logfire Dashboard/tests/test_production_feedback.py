"""Unit tests for production incident feedback loop."""

import pytest
from evals.production_feedback import ingest_production_incident, evaluate_ingested_incident


def test_ingest_production_incident():
    """Verify incident ingestion logs and structures incident case."""
    record = ingest_production_incident(
        incident_id="PROD-TEST-99",
        user_prompt="Where is order A100?",
        bad_agent_output="I don't know.",
        expected_ground_truth="Order A100 is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones.",
        category="production_failure",
        risk="high",
        tags=["incident", "order"],
    )

    assert record["incident_id"] == "PROD-TEST-99"
    assert record["name"] == "prod_incident_prod_test_99"
    assert record["inputs"] == "Where is order A100?"
    assert record["metadata"]["category"] == "production_failure"


@pytest.mark.asyncio
async def test_evaluate_ingested_incident():
    """Verify evaluation of ingested incident against current agent."""
    record = {
        "incident_id": "PROD-TEST-100",
        "name": "prod_incident_prod_test_100",
        "inputs": "Where is order A100?",
        "expected_output": "Order A100 is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones.",
        "metadata": {
            "category": "production_failure",
            "risk": "low",
            "requires_tool": True,
            "expected_tool": "lookup_order",
            "required_keywords": ["A100", "Shipped", "TRK-98765"],
        },
    }

    res = await evaluate_ingested_incident(record)
    assert res["passed"] is True
    assert res["composite_score"] >= 0.85

