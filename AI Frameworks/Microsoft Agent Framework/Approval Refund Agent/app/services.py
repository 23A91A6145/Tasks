import json
from datetime import datetime, date
from typing import Dict, Any, List
from pathlib import Path
from app.models import RefundDashboardStats, ApprovalRequest
from app.approval import get_all_approval_requests
from app.settings import settings
from app.utils import logger

NOTIFICATION_OUTBOX = settings.checkpoint_dir / "notifications.json"


def get_dashboard_stats() -> RefundDashboardStats:
    """Calculates statistics across all refund approval requests in the DB."""
    requests = get_all_approval_requests()

    pending = 0
    approved = 0
    rejected = 0
    escalated = 0
    hold = 0
    expired = 0
    total_processing_time = 0.0
    processed_count = 0
    today_count = 0
    total_value = 0.0

    today_str = date.today().isoformat()

    for req_data in requests.values():
        req = ApprovalRequest(**req_data)

        # Count by status
        if req.status == "Pending":
            pending += 1
        elif req.status == "Approved":
            approved += 1
        elif req.status == "Rejected":
            rejected += 1
        elif req.status == "Escalated":
            escalated += 1
        elif req.status == "Hold":
            hold += 1
        elif req.status == "Expired":
            expired += 1

        # Count today's requests
        if req.created_at.startswith(today_str):
            today_count += 1
            total_value += req.amount

        # Calculate processing time
        if req.status in ["Approved", "Rejected"] and req.handled_at:
            try:
                t_created = datetime.fromisoformat(req.created_at)
                t_handled = datetime.fromisoformat(req.handled_at)
                delta = (t_handled - t_created).total_seconds()
                total_processing_time += max(0.0, delta)
                processed_count += 1
            except Exception as e:
                logger.error(f"Error parsing date times for processing stats: {e}")

    avg_time = (total_processing_time / processed_count) if processed_count > 0 else 0.0

    return RefundDashboardStats(
        pending_count=pending,
        approved_count=approved,
        rejected_count=rejected,
        escalated_count=escalated,
        hold_count=hold,
        avg_processing_time_seconds=avg_time,
        today_requests_count=today_count,
        expired_count=expired,
        today_refund_value=round(total_value, 2),
    )


def generate_notifications(req: ApprovalRequest) -> Dict[str, str]:
    """Generates email templates, internal alerts, and customer confirmations."""
    amount_str = f"${req.amount:.2f}"

    if req.status == "Approved":
        email_subject = f"Refund Processed: Order {req.order_id}"
        email_body = (
            f"Dear Customer,\n\n"
            f"Good news! Your refund request of {amount_str} for Order {req.order_id} has been approved.\n"
            f"Reason: {req.reason}\n"
            f"Transaction Reference: TXN-{req.order_id.split('-')[-1]}-REFUND\n\n"
            f"The funds will be credited back to your original payment method within 3 to 5 business days.\n\n"
            f"Thank you,\nRefunds Operations Team"
        )
        internal_alert = f"✅ REFUND PROCESSED: {amount_str} for Order {req.order_id} has been successfully completed by reviewer {req.reviewer}."

    elif req.status == "Rejected":
        email_subject = f"Refund Request Update: Order {req.order_id}"
        email_body = (
            f"Dear Customer,\n\n"
            f"We have reviewed your refund request of {amount_str} for Order {req.order_id}.\n"
            f"Unfortunately, we are unable to process this refund. Reviewer Notes: {req.notes or 'Does not comply with our refund policy'}.\n\n"
            f"If you believe this was an error or would like to provide more context, please contact customer support.\n\n"
            f"Regards,\nRefunds Operations Team"
        )
        internal_alert = f"❌ REFUND REJECTED: Request for Order {req.order_id} ({amount_str}) was rejected by reviewer {req.reviewer}."

    elif req.status == "Escalated":
        email_subject = ""
        email_body = ""
        internal_alert = f"⚠️ ESCALATION: Refund Request {req.id} ({amount_str}) escalated. Requires Manager review."

    else:
        email_subject = ""
        email_body = ""
        internal_alert = f"ℹ️ STATUS UPDATE: Refund Request {req.id} status changed to {req.status}."

    return {
        "email_subject": email_subject,
        "email_body": email_body,
        "internal_alert": internal_alert,
    }


def save_notification(req: ApprovalRequest) -> Dict[str, str]:
    """Persists a generated notification into the outbox and returns it."""
    notifications = generate_notifications(req)
    if not notifications["email_body"] and not notifications["internal_alert"]:
        return notifications

    entry = {
        "request_id": req.id,
        "order_id": req.order_id,
        "status": req.status,
        "notifications": notifications,
        "timestamp": datetime.now().isoformat(),
    }

    outbox: List[Dict[str, Any]] = []
    if NOTIFICATION_OUTBOX.exists():
        try:
            outbox = json.loads(NOTIFICATION_OUTBOX.read_text())
        except Exception:
            outbox = []

    outbox.append(entry)
    try:
        NOTIFICATION_OUTBOX.write_text(json.dumps(outbox, indent=4))
    except Exception as e:
        logger.error(f"Failed to persist notification outbox: {e}")

    return notifications


def get_notification_outbox() -> List[Dict[str, Any]]:
    """Returns the persisted notification outbox (newest first)."""
    if not NOTIFICATION_OUTBOX.exists():
        return []
    try:
        outbox = json.loads(NOTIFICATION_OUTBOX.read_text())
    except Exception as e:
        logger.error(f"Failed to read notification outbox: {e}")
        return []
    return list(reversed(outbox))
