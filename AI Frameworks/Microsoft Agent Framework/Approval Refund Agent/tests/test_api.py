import os
from fastapi.testclient import TestClient

os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("SEED_DEMO_DATA", "false")

import main as app_module
from app.approval import get_approval_request

client = TestClient(app_module.app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert "framework" in body


def test_info_endpoint():
    res = client.get("/api/info")
    assert res.status_code == 200
    assert "max_auto_approve_amount" in res.json()


def test_stats_endpoint():
    res = client.get("/api/stats")
    assert res.status_code == 200
    body = res.json()
    for key in ("pending_count", "approved_count", "rejected_count", "today_requests_count"):
        assert key in body


def test_root_serves_dashboard():
    res = client.get("/")
    assert res.status_code == 200
    assert "Refund Compliance" in res.text


def test_chat_clarification_flow():
    res = client.post("/api/chat", json={"message": "hi"})
    assert res.status_code == 200
    assert res.json()["status"] == "clarification_required"


def test_chat_creates_approval_then_approve():
    res = client.post(
        "/api/chat",
        json={"message": "Process a refund of $89.99 for CUST-5511 order ORD-3321 because item damaged."},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "approval_required"
    req_id = body["request_id"]
    assert get_approval_request(req_id) is not None

    decision = client.post(
        f"/api/approvals/{req_id}/decision",
        json={
            "action": "Approve",
            "notes": "Verified damage.",
            "reviewer_name": "Alice Smith",
            "reviewer_role": "Reviewer",
        },
        headers={"x-session-id": "SESSION-TEST"},
    )
    assert decision.status_code == 200
    result = decision.json()
    assert result["status"] == "success"
    assert result["req_status"] == "Approved"
    assert result["notifications"]["email_body"]


def test_decision_validation_errors():
    res = client.post(
        "/api/approvals/REF-XXX/decision",
        json={"action": "Approve", "reviewer_name": "Alice", "reviewer_role": "Nope"},
    )
    assert res.status_code == 422


def test_decision_unauthorized_returns_403():
    res = client.post(
        "/api/chat",
        json={"message": "Process a refund of $450 for CUST-2092 order ORD-8812 because no longer needed."},
    )
    req_id = res.json()["request_id"]

    decision = client.post(
        f"/api/approvals/{req_id}/decision",
        json={
            "action": "Approve",
            "reviewer_name": "Alice Smith",
            "reviewer_role": "Reviewer",
        },
    )
    assert decision.status_code == 403


def test_notifications_outbox_endpoint():
    # Create + approve a request so notifications are persisted to the outbox
    res = client.post(
        "/api/chat",
        json={"message": "Process a refund of $60 for CUST-1045 order ORD-5582 due to packaging defect."},
    )
    req_id = res.json()["request_id"]
    client.post(
        f"/api/approvals/{req_id}/decision",
        json={
            "action": "Approve",
            "notes": "OK.",
            "reviewer_name": "Alice Smith",
            "reviewer_role": "Reviewer",
        },
    )
    outbox = client.get("/api/notifications")
    assert outbox.status_code == 200
    assert len(outbox.json()) >= 1


def test_missing_request_returns_404():
    res = client.get("/api/approvals/REF-DOES-NOT-EXIST")
    assert res.status_code == 404
