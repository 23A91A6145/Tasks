import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from app.models import DecisionInput, AuditLogEntry, ApprovalRequest
from app.utils import logger, log_audit, log_error
from app.workflow import WorkflowState
from app.refund_tool import execute_payment_refund
from app.config import BASE_DIR, APPROVAL_SLA_TIMEOUT_SECONDS, SEED_DEMO_DATA

DB_FILE = BASE_DIR / "checkpoints" / "approvals_db.json"

ACTIVE_STATUSES = ("Pending", "Escalated", "Hold", "Request More Info")


def _build_seed_data(now_str: str) -> Dict[str, Any]:
    """Constructs the demo seed dataset."""
    seed_data = {
        "REF-1001": {
                "id": "REF-1001",
                "customer_id": "CUST-1045",
                "order_id": "ORD-3321",
                "amount": 45.00,
                "reason": "Incorrect shipping charges",
                "risk_level": "Low",
                "product": "Neural Net Processor Schematic",
                "purchase_date": "2026-08-03",
                "status": "Approved",
                "reviewer": "Alice Smith",
                "role_required": "Reviewer",
                "notes": "Valid shipping issue. Approved partial refund.",
                "created_at": "2026-08-05T09:15:00",
                "handled_at": "2026-08-05T09:30:00",
                "timeline": [
                    {"step": "Customer Request Received", "timestamp": "2026-08-05T09:15:00"},
                    {"step": "Safety Policies Verified", "timestamp": "2026-08-05T09:16:00"},
                    {"step": "Refund Tool Intercepted (Approval Required)", "timestamp": "2026-08-05T09:17:00"},
                    {"step": "Approved by Human", "timestamp": "2026-08-05T09:30:00"},
                    {"step": "Refund Executed Successfully", "timestamp": "2026-08-05T09:30:00"}
                ]
            },
            "REF-1002": {
                "id": "REF-1002",
                "customer_id": "CUST-1045",
                "order_id": "ORD-5582",
                "amount": 125.00,
                "reason": "Wrong Item Delivered",
                "risk_level": "Low",
                "product": "T-800 CPU Repair Kit",
                "purchase_date": "2026-07-28",
                "status": "Approved",
                "reviewer": "Bob Johnson",
                "role_required": "Manager",
                "notes": "Customer received the wrong repair kit. Approved full refund.",
                "created_at": "2026-08-05T14:22:00",
                "handled_at": "2026-08-05T14:35:00",
                "timeline": [
                    {"step": "Customer Request Received", "timestamp": "2026-08-05T14:22:00"},
                    {"step": "Safety Policies Verified", "timestamp": "2026-08-05T14:23:00"},
                    {"step": "Refund Tool Intercepted (Approval Required)", "timestamp": "2026-08-05T14:24:00"},
                    {"step": "Approved by Human", "timestamp": "2026-08-05T14:35:00"},
                    {"step": "Refund Executed Successfully", "timestamp": "2026-08-05T14:35:00"}
                ]
            },
            "REF-1003": {
                "id": "REF-1003",
                "customer_id": "CUST-9912",
                "order_id": "ORD-0001",
                "amount": 1500.00,
                "reason": "Defective item",
                "risk_level": "High",
                "product": "Sub-zero Nitrogen Container",
                "purchase_date": "2026-08-05",
                "status": "Rejected",
                "reviewer": "Bob Johnson",
                "role_required": "Manager",
                "notes": "Account status flagged as suspicious high risk. Policy rejection.",
                "created_at": "2026-08-06T08:10:00",
                "handled_at": "2026-08-06T08:45:00",
                "timeline": [
                    {"step": "Customer Request Received", "timestamp": "2026-08-06T08:10:00"},
                    {"step": "Safety Policies Verified", "timestamp": "2026-08-06T08:12:00"},
                    {"step": "Refund Tool Intercepted (Approval Required)", "timestamp": "2026-08-06T08:13:00"},
                    {"step": "Rejected by Human", "timestamp": "2026-08-06T08:45:00"},
                    {"step": "Refund Request Cancelled", "timestamp": "2026-08-06T08:45:00"}
                ]
            },
            "REF-1004": {
                "id": "REF-1004",
                "customer_id": "CUST-2092",
                "order_id": "ORD-8812",
                "amount": 450.00,
                "reason": "Late delivery, no longer needed",
                "risk_level": "Medium",
                "product": "Tactical Radio Comm",
                "purchase_date": "2026-08-01",
                "status": "Pending",
                "role_required": "Manager",
                "notes": "",
                "created_at": now_str,
                "timeline": [
                    {"step": "Customer Request Received", "timestamp": now_str},
                    {"step": "Safety Policies Verified", "timestamp": now_str},
                    {"step": "Refund Tool Intercepted (Approval Required)", "timestamp": now_str}
                ]
            },
            "REF-1005": {
                "id": "REF-1005",
                "customer_id": "CUST-5511",
                "order_id": "ORD-3321",
                "amount": 89.99,
                "reason": "Item damaged during shipping",
                "risk_level": "Low",
                "product": "Neural Net Processor Schematic",
                "purchase_date": "2026-08-03",
                "status": "Pending",
                "role_required": "Reviewer",
                "notes": "",
                "created_at": now_str,
                "timeline": [
                    {"step": "Customer Request Received", "timestamp": now_str},
                    {"step": "Safety Policies Verified", "timestamp": now_str},
                    {"step": "Refund Tool Intercepted (Approval Required)", "timestamp": now_str}
                ]
            }
        }
    return seed_data


def _seed_database() -> Dict[str, Any]:
    """Writes the demo seed dataset and matching checkpoints to disk."""
    now_str = datetime.now().isoformat()
    seed_data = _build_seed_data(now_str)
    _save_db(seed_data)

    # Create checkpoints for the pending seeds so their workflows can be resumed
    for ref_id in ["REF-1004", "REF-1005"]:
        req_info = seed_data[ref_id]
        checkpoint_data = {
            "request_id": ref_id,
            "tool_call": {
                "name": "execute_payment_refund",
                "args": {
                    "customer_id": req_info["customer_id"],
                    "order_id": req_info["order_id"],
                    "amount": req_info["amount"],
                    "reason": req_info["reason"]
                }
            },
            "approval_req": req_info,
            "paused_at": req_info["created_at"]
        }
        WorkflowState.save_checkpoint(ref_id, checkpoint_data)

    logger.info("🌱 Database seeded with initial test requests and checkpoints.")
    return seed_data


def _refresh_demo_pending(data: Dict[str, Any], now_str: str) -> Dict[str, Any]:
    """
    Re-arms the seeded demo pending tickets (REF-1004/REF-1005) if they have
    auto-expired via the SLA lease, so the DevUI demo always has a live queue.
    Tickets that a human approved/rejected are never overwritten.
    """
    demo_pending_ids = ("REF-1004", "REF-1005")
    all_expired = all(
        data.get(rid, {}).get("status") == "Expired" for rid in demo_pending_ids
    )
    if not all_expired:
        return data

    seed = _build_seed_data(now_str)
    for rid in demo_pending_ids:
        data[rid] = seed[rid]
        checkpoint_data = {
            "request_id": rid,
            "tool_call": {
                "name": "execute_payment_refund",
                "args": {
                    "customer_id": seed[rid]["customer_id"],
                    "order_id": seed[rid]["order_id"],
                    "amount": seed[rid]["amount"],
                    "reason": seed[rid]["reason"]
                }
            },
            "approval_req": seed[rid],
            "paused_at": now_str
        }
        WorkflowState.save_checkpoint(rid, checkpoint_data)
    _save_db(data)
    logger.info("🔄 Demo pending tickets re-armed with a fresh SLA lease.")
    return data


def _load_db() -> Dict[str, Any]:
    """Loads all approvals, seeding/refreshing demo data and enforcing SLA timeouts."""
    now_str = datetime.now().isoformat()

    if not DB_FILE.exists():
        # Demo seed data is only created when explicitly enabled (config).
        if SEED_DEMO_DATA:
            return _seed_database()
        return {}

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)

        # Keep the demo queue populated when demo mode is enabled
        if SEED_DEMO_DATA:
            data = _refresh_demo_pending(data, now_str)

        # Run auto-expiry check on any active requests (SLA lease)
        now = datetime.now()
        db_modified = False
        for req_id, req_info in list(data.items()):
            if req_info.get("status") in list(ACTIVE_STATUSES):
                try:
                    created_time = datetime.fromisoformat(req_info.get("created_at"))
                    elapsed = (now - created_time).total_seconds()
                    if elapsed > APPROVAL_SLA_TIMEOUT_SECONDS:
                        logger.warning(
                            f"⏰ Request {req_id} review lease expired after {elapsed:.0f}s. Auto-expiring."
                        )
                        req_info["status"] = "Expired"
                        req_info["notes"] = (
                            f"Request expired automatically. Review SLA lease of "
                            f"{APPROVAL_SLA_TIMEOUT_SECONDS}s exceeded."
                        )
                        req_info["handled_at"] = now.isoformat()
                        req_info["timeline"].append(
                            {"step": "Review SLA Lease Expired", "timestamp": now.isoformat()}
                        )

                        # Clean up checkpoint
                        WorkflowState.delete_checkpoint(req_id)
                        db_modified = True

                        # Log error / audit
                        log_error(f"Compliance Violation: Refund Request {req_id} expired before action was taken.")
                except Exception as ex:
                    logger.error(f"Error checking lease timeout for {req_id}: {ex}")

        if db_modified:
            _save_db(data)

        return data
    except Exception as e:
        logger.error(f"Error loading approvals DB: {e}")
        return {}


def _save_db(data: Dict[str, Any]):
    """Helper to save all approvals to JSON database."""
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving approvals DB: {e}")

def save_approval_request(req: ApprovalRequest):
    """Saves or updates an approval request in the database."""
    db = _load_db()
    db[req.id] = req.model_dump()
    _save_db(db)

def get_approval_request(request_id: str) -> Optional[ApprovalRequest]:
    """Retrieves an approval request from the database."""
    db = _load_db()
    data = db.get(request_id)
    if data:
        return ApprovalRequest(**data)
    return None

def get_all_approval_requests() -> Dict[str, Any]:
    """Returns all approval requests."""
    return _load_db()

def get_pending_approvals() -> Dict[str, Any]:
    """Returns only the approvals that still need human attention."""
    db = _load_db()
    return {
        rid: data for rid, data in db.items()
        if data.get("status") in list(ACTIVE_STATUSES)
    }

def handle_approval_decision(
    request_id: str,
    decision: DecisionInput,
    ip_address: str,
    session_id: str
) -> Dict[str, Any]:
    """
    Processes the human decision (Approve/Reject/Hold/Escalate) on a pending refund.
    Performs RBAC checks, executes the sensitive tool on approval, and logs audits.
    """
    # 1. Load the request status
    req = get_approval_request(request_id)
    if not req:
        raise ValueError(f"Approval Request '{request_id}' not found.")
        
    # Check if already processed
    if req.status in ["Approved", "Rejected"]:
        return {
            "status": "error",
            "message": f"Request has already been finalized as '{req.status}'."
        }

    # 2. Check RBAC permissions
    # If standard Reviewer tries to approve a Manager-only request
    if req.role_required == "Manager" and decision.reviewer_role == "Reviewer" and decision.action == "Approve":
        log_error(f"🔒 Security Alert: Standard Reviewer '{decision.reviewer_name}' attempted to approve Manager-only Request '{request_id}'")
        raise PermissionError("Unauthorized: This action requires Manager-level approval.")

    # 3. Load checkpoint state to access tool call details
    checkpoint = WorkflowState.load_checkpoint(request_id)
    if not checkpoint and decision.action in ["Approve", "Reject"]:
        raise FileNotFoundError(f"Checkpoint data missing for request '{request_id}'. Cannot execute tool.")

    now_str = datetime.now().isoformat()
    req.reviewer = decision.reviewer_name
    req.notes = decision.notes
    req.handled_at = now_str

    result_msg = ""
    tool_result = None

    if decision.action == "Approve":
        # Resume Workflow: Execute the sensitive payment tool
        tool_args = checkpoint["tool_call"]["args"]
        try:
            tool_result = execute_payment_refund(**tool_args)
            req.status = "Approved"
            req.timeline.append({"step": "Approved by Human", "timestamp": now_str})
            req.timeline.append({"step": "Refund Executed Successfully", "timestamp": now_str})
            result_msg = f"Refund approved and executed. Gateway reference: {tool_result['transaction_id']}"
        except Exception as e:
            req.status = "Failed"
            req.timeline.append({"step": "Execution Failed", "timestamp": now_str})
            log_error(f"Refund execution failed for Request '{request_id}': {e}")
            raise e
        finally:
            # Clean up checkpoint
            WorkflowState.delete_checkpoint(request_id)

    elif decision.action == "Reject":
        # Cancel Workflow
        req.status = "Rejected"
        req.timeline.append({"step": "Rejected by Human", "timestamp": now_str})
        req.timeline.append({"step": "Refund Request Cancelled", "timestamp": now_str})
        result_msg = "Refund request rejected. Transaction cancelled."
        # Clean up checkpoint
        WorkflowState.delete_checkpoint(request_id)

    elif decision.action == "Hold":
        req.status = "Hold"
        req.timeline.append({"step": "Placed on Hold", "timestamp": now_str})
        result_msg = "Request placed on hold for further verification."
        # Keep checkpoint intact so it can be resumed later

    elif decision.action == "Escalate":
        req.status = "Escalated"
        req.role_required = "Manager"
        req.timeline.append({"step": "Escalated to Manager", "timestamp": now_str})
        result_msg = "Request escalated to Manager tier."
        # Keep checkpoint intact and update database

    elif decision.action == "Request More Info":
        req.status = "Request More Info"
        req.timeline.append({"step": "Request More Info Sent", "timestamp": now_str})
        result_msg = "Reviewer requested more info from customer."
        # Keep checkpoint intact

    else:
        raise ValueError(f"Unknown approval action '{decision.action}'")

    # Save request state back to DB
    save_approval_request(req)

    # 4. Write secure Audit Log Entry for final decisions
    if req.status in ["Approved", "Rejected"]:
        audit_entry = AuditLogEntry(
            timestamp=now_str,
            request_id=request_id,
            customer_id=req.customer_id,
            order_id=req.order_id,
            amount=req.amount,
            decision=req.status,
            reason=req.reason,
            reviewer=decision.reviewer_name,
            reviewer_role=decision.reviewer_role,
            notes=decision.notes,
            ip_address=ip_address,
            session_id=session_id
        )
        log_audit(audit_entry.model_dump())

    return {
        "status": "success",
        "action": decision.action,
        "message": result_msg,
        "req_status": req.status,
        "tool_result": tool_result
    }
