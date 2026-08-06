import os
import glob
import pytest
from datetime import datetime, timedelta

from app.agent import ChatAgent
from app.approval import (
    handle_approval_decision,
    get_approval_request,
    get_pending_approvals,
    _load_db,
    _save_db,
    save_approval_request,
)
from app.models import DecisionInput, ApprovalRequest
from app.workflow import WorkflowState
from app.config import CHECKPOINT_DIR
from app.services import generate_notifications, get_dashboard_stats
from app.refund_tool import validate_policy, validate_refund_input, execute_payment_refund
from app.utils import MOCK_CUSTOMERS, MOCK_ORDERS


def _create_pending_request(agent, message):
    res = agent.run(message)
    assert res["status"] == "approval_required", res
    save_approval_request(res["approval_req"])
    return res


@pytest.fixture()
def agent():
    return ChatAgent("TestAgent", "Test instructions")


# ---------------------------------------------------------------------------
# Phase 4.5 - Reject flow
# ---------------------------------------------------------------------------
def test_reject_flow(agent):
    res = _create_pending_request(
        agent, "Process a refund of $80 for CUST-1045 order ORD-5582 due to wrong color."
    )
    req_id = res["request_id"]
    assert WorkflowState.load_checkpoint(req_id) is not None

    decision = DecisionInput(
        action="Reject",
        notes="Customer photos do not match item condition.",
        reviewer_name="Alice Smith",
        reviewer_role="Reviewer",
    )
    result = handle_approval_decision(req_id, decision, "127.0.0.1", "TEST-SESSION")

    assert result["status"] == "success"
    assert result["req_status"] == "Rejected"

    req = get_approval_request(req_id)
    assert req.status == "Rejected"
    assert "Rejected by Human" in [s["step"] for s in req.timeline]
    # Checkpoint must be purged to prevent double execution
    assert WorkflowState.load_checkpoint(req_id) is None
    # Rejection generates a customer notification
    notif = generate_notifications(req)
    assert "unable to process" in notif["email_body"].lower()


# ---------------------------------------------------------------------------
# Phase 4.5 - Invalid / policy-rejected refunds
# ---------------------------------------------------------------------------
def test_invalid_refund_unknown_customer(agent):
    res = agent.run("Process a refund of $50 for CUST-9999 order ORD-5582.")
    assert res["status"] == "policy_rejected"
    assert "not found" in res["message"].lower()


def test_invalid_refund_amount_exceeds_order(agent):
    res = agent.run("Process a refund of $900 for CUST-1045 order ORD-5582.")
    assert res["status"] == "policy_rejected"
    assert "exceeds original order amount" in res["message"]


def test_invalid_refund_malformed_input(agent):
    # Unparseable IDs surface as a clarification request (agent asks for valid IDs)
    res = agent.run("Process a refund of $50 for customer 9999 order ORD-5582.")
    assert res["status"] == "clarification_required"
    assert res["missing_fields"]["customer_id"] is True

    # Structural validation still rejects garbage when reached directly
    from app.refund_tool import validate_refund_input
    assert validate_refund_input("1045", "ORD-5582", 50.0)[0] is False


def test_missing_fields_clarification(agent):
    res = agent.run("I want a refund please.")
    assert res["status"] == "clarification_required"
    assert res["missing_fields"]["customer_id"] is True


# ---------------------------------------------------------------------------
# Phase 4.5 - Large amount refund (Manager gate)
# ---------------------------------------------------------------------------
def test_large_amount_requires_manager(agent):
    res = _create_pending_request(
        agent, "Process a refund of $450 for CUST-2092 order ORD-8812 because no longer needed."
    )
    assert res["approval_req"].role_required == "Manager"

    req_id = res["request_id"]
    # Standard Reviewer blocked
    with pytest.raises(PermissionError):
        handle_approval_decision(
            req_id,
            DecisionInput(action="Approve", reviewer_name="Alice Smith", reviewer_role="Reviewer"),
            "127.0.0.1",
            "SESSION-TEST",
        )
    # Manager approves
    result = handle_approval_decision(
        req_id,
        DecisionInput(
            action="Approve",
            reviewer_name="Bob Johnson",
            reviewer_role="Manager",
            notes="Confirmed hardware failure, senior sign-off.",
        ),
        "127.0.0.1",
        "SESSION-TEST",
    )
    assert result["req_status"] == "Approved"
    assert result["tool_result"]["status"] == "success"


# ---------------------------------------------------------------------------
# Hold / Escalate / Request More Info transitions
# ---------------------------------------------------------------------------
def test_hold_then_resume(agent):
    res = _create_pending_request(
        agent, "Process a refund of $70 for CUST-1045 order ORD-5582 due to late delivery."
    )
    req_id = res["request_id"]

    # Hold keeps the checkpoint intact
    handle_approval_decision(
        req_id,
        DecisionInput(action="Hold", notes="Awaiting photos.", reviewer_name="Alice Smith"),
        "127.0.0.1",
        "SESSION-TEST",
    )
    assert get_approval_request(req_id).status == "Hold"
    assert WorkflowState.load_checkpoint(req_id) is not None

    # Then approve resumes the workflow and executes
    result = handle_approval_decision(
        req_id,
        DecisionInput(action="Approve", notes="Photos received, looks valid.", reviewer_name="Alice Smith"),
        "127.0.0.1",
        "SESSION-TEST",
    )
    assert result["req_status"] == "Approved"
    assert WorkflowState.load_checkpoint(req_id) is None


def test_escalation_promotes_to_manager(agent):
    res = _create_pending_request(
        agent, "Process a refund of $60 for CUST-2092 order ORD-8812 due to faulty radio."
    )
    req_id = res["request_id"]
    assert get_approval_request(req_id).role_required == "Reviewer"

    handle_approval_decision(
        req_id,
        DecisionInput(action="Escalate", notes="Medium risk customer, escalate.", reviewer_name="Alice Smith"),
        "127.0.0.1",
        "SESSION-TEST",
    )
    req = get_approval_request(req_id)
    assert req.status == "Escalated"
    assert req.role_required == "Manager"
    # Manager can now approve
    result = handle_approval_decision(
        req_id,
        DecisionInput(action="Approve", reviewer_name="Bob Johnson", reviewer_role="Manager"),
        "127.0.0.1",
        "SESSION-TEST",
    )
    assert result["req_status"] == "Approved"


def test_request_more_info(agent):
    res = _create_pending_request(
        agent, "Process a refund of $60 for CUST-1045 order ORD-5582 due to packaging issue."
    )
    req_id = res["request_id"]
    handle_approval_decision(
        req_id,
        DecisionInput(action="Request More Info", notes="Need invoice copy.", reviewer_name="Alice Smith"),
        "127.0.0.1",
        "SESSION-TEST",
    )
    assert get_approval_request(req_id).status == "Request More Info"
    assert WorkflowState.load_checkpoint(req_id) is not None


# ---------------------------------------------------------------------------
# Anti-fraud: duplicate + double-spend prevention
# ---------------------------------------------------------------------------
def test_double_approve_is_blocked(agent):
    res = _create_pending_request(
        agent, "Process a refund of $60 for CUST-1045 order ORD-5582 due to scratch."
    )
    req_id = res["request_id"]
    decision = DecisionInput(action="Approve", reviewer_name="Alice Smith")

    first = handle_approval_decision(req_id, decision, "127.0.0.1", "SESSION-TEST")
    assert first["req_status"] == "Approved"

    second = handle_approval_decision(req_id, decision, "127.0.0.1", "SESSION-TEST")
    assert second["status"] == "error"
    assert "already been finalized" in second["message"]


# ---------------------------------------------------------------------------
# SLA timeout recovery
# ---------------------------------------------------------------------------
def test_sla_timeout_marks_expired_and_purges(agent):
    res = _create_pending_request(
        agent, "Process a refund of $55 for CUST-1045 order ORD-5582 due to delay."
    )
    req_id = res["request_id"]

    # Backdate created_at to simulate > SLA timeout
    db = _load_db()
    past = (datetime.now() - timedelta(minutes=10)).isoformat()
    db[req_id]["created_at"] = past
    _save_db(db)

    data = _load_db()  # triggers expiry check
    assert data[req_id]["status"] == "Expired"
    assert "SLA" in data[req_id]["notes"]
    assert WorkflowState.load_checkpoint(req_id) is None
    assert req_id not in get_pending_approvals()


# ---------------------------------------------------------------------------
# Policy engine unit tests
# ---------------------------------------------------------------------------
def test_policy_engine_edge_cases():
    # High-risk customer always requires Manager
    assert validate_policy("CUST-9912", "ORD-0001", 10.0)[2] == "Manager"
    # Suspended account rejected (simulate by direct dict tweak is not possible; use CUST-9912 flagged)
    ok, reason, role = validate_policy("CUST-1045", "ORD-8812", 10.0)
    assert ok is False and "does not belong" in reason
    # Zero / negative amounts rejected
    assert validate_policy("CUST-1045", "ORD-5582", 0.0)[0] is False
    assert validate_policy("CUST-1045", "ORD-5582", -5.0)[0] is False
    # Malformed input rejected at the boundary
    assert validate_refund_input("1045", "ORD-5582", 50.0)[0] is False
    assert validate_refund_input("CUST-1045", "ORD-5582", 0)[0] is False
    assert validate_refund_input("CUST-1045", "ORD-5582", "not-a-number")[0] is False
    # Refund ceiling
    assert validate_refund_input("CUST-1045", "ORD-5582", 2_000_000)[0] is False


def test_execute_payment_refund_invariants():
    # Tool refuses obviously invalid amounts at the gateway boundary
    with pytest.raises(ValueError):
        execute_payment_refund("CUST-1045", "ORD-5582", -1, "test")
    result = execute_payment_refund("CUST-1045", "ORD-5582", 45.0, "test")
    assert result["status"] == "success"
    assert result["transaction_id"].startswith("TXN-")


# ---------------------------------------------------------------------------
# Dashboard statistics
# ---------------------------------------------------------------------------
def test_dashboard_stats(agent):
    _create_pending_request(agent, "Process a refund of $80 for CUST-1045 order ORD-5582 due to issue.")
    res2 = _create_pending_request(agent, "Process a refund of $450 for CUST-2092 order ORD-8812 due to fault.")
    handle_approval_decision(
        res2["request_id"],
        DecisionInput(action="Approve", reviewer_name="Bob Johnson", reviewer_role="Manager"),
        "127.0.0.1",
        "SESSION-TEST",
    )
    stats = get_dashboard_stats()
    assert stats.pending_count >= 1
    assert stats.approved_count >= 1
    assert stats.avg_processing_time_seconds >= 0
