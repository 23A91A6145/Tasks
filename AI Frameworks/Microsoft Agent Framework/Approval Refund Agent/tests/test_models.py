import pytest
from pydantic import ValidationError

from app.models import RefundRequest, DecisionInput, ApprovalRequest, AuditLogEntry


def test_refund_request_valid():
    req = RefundRequest(customer_id="cust-1045", order_id="ord-5582", amount=45.5, reason="test")
    # Normalizes IDs to uppercase
    assert req.customer_id == "CUST-1045"
    assert req.order_id == "ORD-5582"


def test_refund_request_invalid_amount():
    with pytest.raises(ValidationError):
        RefundRequest(customer_id="CUST-1045", order_id="ORD-5582", amount=0)
    with pytest.raises(ValidationError):
        RefundRequest(customer_id="CUST-1045", order_id="ORD-5582", amount=-5)
    with pytest.raises(ValidationError):
        RefundRequest(customer_id="CUST-1045", order_id="ORD-5582", amount=2_000_000)


def test_refund_request_invalid_ids():
    with pytest.raises(ValidationError):
        RefundRequest(customer_id="1045", order_id="ORD-5582", amount=10)
    with pytest.raises(ValidationError):
        RefundRequest(customer_id="CUST-1045", order_id="abc", amount=10)


def test_decision_input_action_constraint():
    with pytest.raises(ValidationError):
        DecisionInput(action="Delete", reviewer_name="Alice")
    with pytest.raises(ValidationError):
        DecisionInput(action="Approve", reviewer_role="CEO", reviewer_name="Alice")


def test_approval_request_defaults():
    req = ApprovalRequest(
        id="REF-1",
        customer_id="CUST-1045",
        order_id="ORD-5582",
        amount=10.0,
        reason="r",
        risk_level="Low",
        product="p",
        purchase_date="2026-01-01",
        created_at="2026-01-01T00:00:00",
    )
    assert req.status == "Pending"
    assert req.role_required == "Reviewer"
    assert req.notes == ""
