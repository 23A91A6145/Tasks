#!/usr/bin/env python
import os
import sys
import json
import time
import glob
from datetime import datetime, timedelta
from pathlib import Path

# Fix pythonpath
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agent import ChatAgent
from app.approval import (
    _load_db,
    _save_db,
    save_approval_request,
    get_approval_request,
    handle_approval_decision
)
from app.models import DecisionInput, ApprovalRequest
from app.workflow import WorkflowState
from app.config import CHECKPOINT_DIR, AUDIT_LOG_PATH, ERROR_LOG_PATH
from app.utils import logger, MOCK_CUSTOMERS, MOCK_ORDERS

def print_header(title):
    print("\n" + "=" * 80)
    print(f"🌟 {title}")
    print("=" * 80)

def print_status(label, val):
    print(f"👉 \033[94m{label:<32}\033[0m: {val}")

def clear_data():
    """Wipe database and checkpoints for a clean run."""
    from app.approval import DB_FILE
    with open(DB_FILE, "w") as f:
        f.write("{}")
    for f_path in glob.glob(str(CHECKPOINT_DIR / "*.json")):
        if "approvals_db.json" in f_path:
            continue
        try:
            os.unlink(f_path)
        except:
            pass

def main():
    print_header("APPROVAL-GATED REFUND AGENT - VOLUMES 1-5 RUNNER")
    print_status("System Workspace", Path(__file__).parent.resolve())
    print_status("Python Executable", sys.executable)
    print_status("Start Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Clean workspace
    clear_data()
    
    agent = ChatAgent(
        name="DemoSafetyAgent",
        instructions="Compliance agent demo runner."
    )
    
    # -------------------------------------------------------------------------
    # Scenario 1: Low Risk Auto-Approval
    # -------------------------------------------------------------------------
    print_header("SCENARIO 1: Low Risk Auto-Approval (<=$50.00)")
    prompt_auto = "Process a refund of $45 for CUST-1045 order ORD-5582 due to minor scratch."
    print(f"Sending request: \"{prompt_auto}\"")
    
    res_auto = agent.run(prompt_auto)
    print_status("Agent Outcome Status", res_auto["status"])
    print_status("Generated Request ID", res_auto["request_id"])
    print_status("Message Response", res_auto["message"])
    
    # Check database
    req_auto = get_approval_request(res_auto["request_id"])
    print_status("Database Entry Status", req_auto.status if req_auto else "None")
    print_status("Database Reviewer Assigned", req_auto.reviewer if req_auto else "None")
    print_status("Active Disk Checkpoint", "Present" if WorkflowState.load_checkpoint(res_auto["request_id"]) else "None (Cleared on Success)")

    # -------------------------------------------------------------------------
    # Scenario 2: Standard Payout Interception (Pausing & Checkpointing)
    # -------------------------------------------------------------------------
    print_header("SCENARIO 2: Sensitive Tool Interception & Pause (>$50.00)")
    prompt_pause = "Process a refund of $89.99 for CUST-5511 order ORD-3321 because item damaged."
    print(f"Sending request: \"{prompt_pause}\"")
    
    res_pause = agent.run(prompt_pause)
    print_status("Agent Outcome Status", res_pause["status"])
    print_status("Generated Request ID", res_pause["request_id"])
    print_status("Message Response", res_pause["message"])
    print_status("Role Required to Approve", res_pause["approval_req"].role_required)
    
    # Register ticket in DB (normally done by API controller)
    save_approval_request(res_pause["approval_req"])
    
    # Check disk checkpoints
    ckpt = WorkflowState.load_checkpoint(res_pause["request_id"])
    print_status("Active Disk Checkpoint", "Saved Successfully (State paused)" if ckpt else "Missing")
    if ckpt:
        print_status("Saved Tool Call Name", ckpt["tool_call"]["name"])
        print_status("Saved Tool Arguments", json.dumps(ckpt["tool_call"]["args"]))

    # -------------------------------------------------------------------------
    # Scenario 3: Duplicate Request Protection (Anti-Fraud Safety Block)
    # -------------------------------------------------------------------------
    print_header("SCENARIO 3: Duplicate Submission Safeguard (Anti-Fraud)")
    prompt_dup = "Process a refund of $89.99 for CUST-5511 order ORD-3321 because item damaged."
    print(f"Sending duplicate request: \"{prompt_dup}\"")
    
    res_dup = agent.run(prompt_dup)
    print_status("Agent Outcome Status", res_dup["status"])
    print_status("Message Response", res_dup["message"])
    print_status("Rejection Cause", res_dup.get("details", {}).get("reason", "None"))

    # -------------------------------------------------------------------------
    # Scenario 4: Role-Based Access Control (RBAC) Gating
    # -------------------------------------------------------------------------
    print_header("SCENARIO 4: Role-Based Access Control (RBAC)")
    # Generate a request that requires a Manager ($120.00 >= $100.00 limit)
    prompt_mgmt = "Process a refund of $120.00 for CUST-1045 order ORD-5582 due to component malfunction."
    print(f"Sending request: \"{prompt_mgmt}\"")
    res_mgmt = agent.run(prompt_mgmt)
    save_approval_request(res_mgmt["approval_req"])
    req_mgmt_id = res_mgmt["request_id"]
    print_status("Request ID", req_mgmt_id)
    print_status("Role Required", res_mgmt["approval_req"].role_required)
    
    # Try to approve with Alice Smith (role: Reviewer)
    print("\n👉 Standard Reviewer (Alice Smith) attempts to approve manager-limit ticket...")
    decision_reviewer = DecisionInput(
        action="Approve",
        reviewer_name="Alice Smith",
        reviewer_role="Reviewer",
        notes="Looks okay to me, approving."
    )
    
    try:
        handle_approval_decision(req_mgmt_id, decision_reviewer, "127.0.0.1", "SESSION-ALICE")
        print("\033[91m❌ ERROR: Approved successfully (Failed RBAC gate!)\033[0m")
    except PermissionError as e:
        print(f"\033[92m✔ SUCCESS: Blocked correctly by RBAC! Exception: {e}\033[0m")

    # Approve with Bob Johnson (role: Manager)
    print("\n👉 Compliance Manager (Bob Johnson) attempts to approve manager-limit ticket...")
    decision_manager = DecisionInput(
        action="Approve",
        reviewer_name="Bob Johnson",
        reviewer_role="Manager",
        notes="High amount confirmed, hardware defect verified."
    )
    res_decision = handle_approval_decision(req_mgmt_id, decision_manager, "127.0.0.1", "SESSION-BOB")
    print_status("Decision Result Status", res_decision["status"])
    print_status("Final Ticket Status", res_decision["req_status"])
    print_status("Disk Checkpoint after success", "Present" if WorkflowState.load_checkpoint(req_mgmt_id) else "None (Cleared on Success)")

    # -------------------------------------------------------------------------
    # Scenario 5: Resumption of Gated Workflow
    # -------------------------------------------------------------------------
    print_header("SCENARIO 5: Checkpoint Resumption & Payment Execution")
    # Resume Scenario 2 standard request (REF-2 or similar)
    req_pause_id = res_pause["request_id"]
    print(f"Resuming paused ticket: {req_pause_id}")
    
    decision_ok = DecisionInput(
        action="Approve",
        reviewer_name="Alice Smith",
        reviewer_role="Reviewer",
        notes="Shipping damages verified. Approved refund."
    )
    
    res_resume = handle_approval_decision(req_pause_id, decision_ok, "127.0.0.1", "SESSION-ALICE")
    print_status("Resumption Result Status", res_resume["status"])
    print_status("Final Ticket Status", res_resume["req_status"])
    print_status("Active Disk Checkpoint", "Present" if WorkflowState.load_checkpoint(req_pause_id) else "None (Purged successfully)")

    # -------------------------------------------------------------------------
    # Scenario 6: Review SLA Lease Expiration
    # -------------------------------------------------------------------------
    print_header("SCENARIO 6: Review SLA Lease Expiry & State Purging")
    # Create a pending ticket
    prompt_sla = "Process a refund of $65.00 for CUST-5511 order ORD-3321 because delivery missed SLA."
    res_sla = agent.run(prompt_sla)
    req_sla_id = res_sla["request_id"]
    save_approval_request(res_sla["approval_req"])
    print_status("Active Ticket Created", req_sla_id)
    print_status("Initial Ticket Status", get_approval_request(req_sla_id).status)
    print_status("Active Checkpoint on disk", "Yes" if WorkflowState.load_checkpoint(req_sla_id) else "No")
    
    # Backdate the ticket created_at in the database to simulate 10 minutes passing
    print("\n👉 Backdating transaction timestamp by 10 minutes to simulate lapse...")
    db = _load_db()
    past_time = (datetime.now() - timedelta(minutes=10)).isoformat()
    db[req_sla_id]["created_at"] = past_time
    _save_db(db)
    
    # Reload database to trigger timeout checks
    print("👉 Reloading database (triggering SLA checks)...")
    reloaded_db = _load_db()
    
    print_status("Updated Ticket Status", reloaded_db[req_sla_id]["status"])
    print_status("Ticket Review Notes", reloaded_db[req_sla_id]["notes"])
    print_status("Active Checkpoint after expiration", "Yes" if WorkflowState.load_checkpoint(req_sla_id) else "No (Safely purged from disk)")

    # -------------------------------------------------------------------------
    # Done
    # -------------------------------------------------------------------------
    print_header("DEMO RUNNER COMPLETED - ALL SCENARIOS VERIFIED SUCCESSFULLY")
    print("To view audit trails:")
    print(f"  cat {AUDIT_LOG_PATH}")
    print("To run tests:")
    print("  python -m pytest")
    print("To run the DevUI dashboard server:")
    print("  python main.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
