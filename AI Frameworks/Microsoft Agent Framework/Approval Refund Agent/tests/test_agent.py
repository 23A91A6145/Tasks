import os
import pytest
from app.agent import ChatAgent
from app.approval import handle_approval_decision, get_approval_request, _load_db, _save_db, save_approval_request
from app.models import DecisionInput
from app.refund_tool import validate_policy
from app.workflow import WorkflowState

@pytest.fixture(autouse=True)
def clean_db():
    """Wipes the DB file and checkpoint files for clean tests."""
    from app.approval import DB_FILE
    import glob
    from app.config import CHECKPOINT_DIR
    
    # Initialize empty DB
    with open(DB_FILE, "w") as f:
        f.write("{}")
        
    # Clear checkpoints folder
    for f_path in glob.glob(str(CHECKPOINT_DIR / "*.json")):
        if "approvals_db.json" in f_path:
            continue
        try:
            import os
            os.unlink(f_path)
        except:
            pass

def test_heuristic_parsing():
    agent = ChatAgent("TestAgent", "Instructions")
    
    # Natural language query 1
    msg1 = "Refund $125 for customer CUST-1045 order ORD-5582 due to wrong item shipped."
    cust, order, amount, reason = agent.extract_refund_details(msg1)
    
    assert cust == "CUST-1045"
    assert order == "ORD-5582"
    assert amount == 125.0
    assert "wrong item" in reason.lower()

    # Query 2 (different format)
    msg2 = "Please process refund for order ORD-8812, customer is CUST-2092. The amount is 450.00 because late delivery."
    cust, order, amount, reason = agent.extract_refund_details(msg2)
    
    assert cust == "CUST-2092"
    assert order == "ORD-8812"
    assert amount == 450.0
    assert "late delivery" in reason.lower()

def test_policy_validations():
    # Valid low risk request
    valid, msg, role = validate_policy("CUST-1045", "ORD-5582", 80.0)
    assert valid is True
    assert role == "Reviewer"

    # High amount request -> requires Manager role
    valid, msg, role = validate_policy("CUST-1045", "ORD-5582", 125.0)
    assert valid is True
    assert role == "Manager"

    # High risk customer -> requires Manager role
    valid, msg, role = validate_policy("CUST-9912", "ORD-0001", 50.0)
    assert valid is True
    assert role == "Manager"

    # Invalid amount exceeds order amount
    valid, msg, role = validate_policy("CUST-1045", "ORD-5582", 200.0)
    assert valid is False
    assert "exceeds original order amount" in msg

    # Customer/Order mismatch
    valid, msg, role = validate_policy("CUST-1045", "ORD-8812", 50.0)
    assert valid is False
    assert "does not belong to Customer" in msg

def test_workflow_pause_and_resume():
    agent = ChatAgent("TestAgent", "Instructions")
    msg = "Process a refund of $89.99 for CUST-5511 order ORD-3321 due to damaged item."
    res = agent.run(msg)
    save_approval_request(res["approval_req"])
    
    assert res["status"] == "approval_required"
    req_id = res["request_id"]
    
    # Verify checkpoint exists
    checkpoint = WorkflowState.load_checkpoint(req_id)
    assert checkpoint is not None
    assert checkpoint["tool_call"]["name"] == "execute_payment_refund"
    assert checkpoint["tool_call"]["args"]["amount"] == 89.99

    # Approve decision (Standard Reviewer)
    decision = DecisionInput(
        action="Approve",
        notes="Looks good. Valid damaged item photo.",
        reviewer_name="Alice Smith",
        reviewer_role="Reviewer"
    )
    
    db_res = handle_approval_decision(req_id, decision, "127.0.0.1", "TEST-SESSION")
    assert db_res["status"] == "success"
    assert db_res["req_status"] == "Approved"
    
    # Checkpoint should be cleaned up
    assert WorkflowState.load_checkpoint(req_id) is None

def test_role_based_access_control():
    agent = ChatAgent("TestAgent", "Instructions")
    
    # Trigger high amount refund (Manager required)
    msg = "Process a refund of $450 for CUST-2092 order ORD-8812 because no longer needed"
    res = agent.run(msg)
    save_approval_request(res["approval_req"])
    
    assert res["status"] == "approval_required"
    req_id = res["request_id"]
    
    # Reviewer tries to approve Manager limit -> expect PermissionError
    decision = DecisionInput(
        action="Approve",
        notes="Attempting approval.",
        reviewer_name="Alice Smith",
        reviewer_role="Reviewer"
    )
    
    with pytest.raises(PermissionError):
        handle_approval_decision(req_id, decision, "127.0.0.1", "TEST-SESSION")
        
    # Manager tries to approve -> success
    decision.reviewer_role = "Manager"
    decision.reviewer_name = "Bob Johnson"
    
    db_res = handle_approval_decision(req_id, decision, "127.0.0.1", "TEST-SESSION")
    assert db_res["status"] == "success"
    assert db_res["req_status"] == "Approved"

def test_auto_approval():
    from app.config import MAX_AUTO_APPROVE_AMOUNT
    assert MAX_AUTO_APPROVE_AMOUNT == 50.00

    agent = ChatAgent("TestAgent", "Instructions")
    
    # Trigger a low amount refund for low risk customer CUST-1045, order ORD-5582 (amount $45.00 <= $50.00)
    msg = "Process a refund of $45.00 for CUST-1045 order ORD-5582 because incorrect shipping fee."
    res = agent.run(msg)
    
    # It should be auto-approved directly!
    assert res["status"] == "auto_approved"
    req_id = res["request_id"]
    
    # Check that it is already in status "Approved" in the database
    req = get_approval_request(req_id)
    assert req is not None
    assert req.status == "Approved"
    assert req.reviewer == "System (Auto-Approve)"
    
    # No checkpoint should be left on disk since it executed immediately
    assert WorkflowState.load_checkpoint(req_id) is None

def test_duplicate_refund_prevention():
    agent = ChatAgent("TestAgent", "Instructions")
    
    # Create first valid request (paused, pending)
    msg1 = "Process a refund of $60.00 for CUST-1045 order ORD-5582 because defective packaging."
    res1 = agent.run(msg1)
    assert res1["status"] == "approval_required"
    save_approval_request(res1["approval_req"])
    
    # Send a duplicate request for the same order
    msg2 = "Process a refund of $60.00 for CUST-1045 order ORD-5582 because duplicate claim."
    res2 = agent.run(msg2)
    
    # It should be rejected as duplicate
    assert res2["status"] == "policy_rejected"
    assert "duplicate" in res2["message"].lower()

def test_timeout_recovery():
    import time
    # Create a request directly in DB and set creation timestamp to 1 hour ago
    req_id = "REF-OLD-TICKET"
    from app.models import ApprovalRequest
    from datetime import datetime, timedelta
    
    past_time = (datetime.now() - timedelta(minutes=10)).isoformat()
    old_req = ApprovalRequest(
        id=req_id,
        customer_id="CUST-1045",
        order_id="ORD-5582",
        amount=30.00,
        reason="Shipping delay",
        risk_level="Low",
        product="T-800 CPU Repair Kit",
        purchase_date="2026-07-28",
        status="Pending",
        role_required="Reviewer",
        created_at=past_time,
        timeline=[{"step": "Customer Request Received", "timestamp": past_time}]
    )
    
    # Save request and mock checkpoint
    save_approval_request(old_req)
    checkpoint_data = {
        "request_id": req_id,
        "tool_call": {
            "name": "execute_payment_refund",
            "args": {"customer_id": "CUST-1045", "order_id": "ORD-5582", "amount": 30.0, "reason": "Shipping delay"}
        },
        "approval_req": old_req.model_dump(),
        "paused_at": past_time
    }
    WorkflowState.save_checkpoint(req_id, checkpoint_data)
    
    # Load database (which triggers auto-expiration checks)
    data = _load_db()
    
    # Ticket status should now be Expired
    assert data[req_id]["status"] == "Expired"
    assert "SLA" in data[req_id]["notes"]
    
    # Checkpoint should be deleted
    assert WorkflowState.load_checkpoint(req_id) is None


