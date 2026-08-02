"""Ticket flow — the flagship checkpointed workflow.

start → classify (AI engine) → [escalate? → awaiting_approval] → publish → done

If the AI decides the ticket needs a human, or the tenant requires approval,
the flow pauses at ``awaiting_approval``. A manager resumes it via
``POST /flows/{run_id}/resume`` and the reply is published from the saved
checkpoint. Nothing is lost between runs — state lives in FlowRun.checkpoint.
"""

from typing import Optional

from sqlalchemy.orm import Session

from ..agents import handle_ticket as ai_handle_ticket
from ..core.permissions import ROLE_MANAGER
from ..models import FlowRun, Organization, Ticket, User
from ..services import audit
from . import runner


def _publish(db: Session, organization: Organization, run: FlowRun, ticket: Ticket) -> None:
    checkpoint = run.checkpoint
    from ..models import TicketMessage

    ticket.classification = checkpoint.get("classification", ticket.classification)
    ticket.priority = checkpoint.get("priority", ticket.priority)
    ticket.ai_summary = checkpoint.get("summary", ticket.ai_summary)

    db.add(
        TicketMessage(
            ticket_id=ticket.id,
            sender="ai",
            content=checkpoint.get("draft", ""),
            meta_json={
                "flow_run_id": run.id,
                "engine": checkpoint.get("engine", "fallback"),
                "sources": checkpoint.get("sources", []),
                "approved": checkpoint.get("approved", True),
            },
        )
    )

    if checkpoint.get("escalate"):
        ticket.status = "escalated"
    else:
        ticket.status = "resolved"
        ticket.resolved_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)

    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=ticket.created_by_id,
        action="ticket.ai_resolved",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata={"flow_run": run.id, "engine": checkpoint.get("engine"), "escalated": bool(checkpoint.get("escalate"))},
    )
    runner.set_output(db, run, ticket_id=ticket.id, status=ticket.status)


def run_ticket_flow(
    db: Session,
    organization: Organization,
    ticket: Ticket,
    user: Optional[User] = None,
    require_approval: bool = False,
) -> FlowRun:
    """Create a ticket flow run and execute up to the first checkpoint."""
    run = runner.create_run(
        db,
        organization,
        "ticket",
        {"ticket_id": ticket.id, "subject": ticket.subject},
        user=user,
    )

    result = ai_handle_ticket(db, organization, ticket.subject, ticket.body)
    from ..services import usage

    usage.track(
        db,
        organization_id=organization.id,
        user_id=user.id if user else None,
        kind="flow",
        model=result.engine,
        units=1,
        meta={"action": "ticket.handle", "classification": result.classification, "priority": result.priority},
    )
    run.checkpoint = {
        "classification": result.classification,
        "priority": result.priority,
        "draft": result.draft,
        "summary": result.summary,
        "sources": result.sources,
        "escalate": result.escalate,
        "confidence": result.confidence,
        "engine": result.engine,
        "approved": False,
    }
    runner.set_step(db, run, "publish")

    needs_approval = result.escalate or require_approval
    if needs_approval:
        runner.set_status(db, run, "awaiting_approval")
        audit.log_activity(
            db,
            organization_id=organization.id,
            user_id=user.id if user else None,
            action="flow.ticket.awaiting_approval",
            entity_type="flow_run",
            entity_id=run.id,
            metadata={"ticket_id": ticket.id, "reason": "escalation" if result.escalate else "approval required"},
        )
    else:
        _publish(db, organization, run, ticket)
        runner.set_status(db, run, "completed")

    db.commit()
    db.refresh(run)
    return run


def resume_ticket_flow(
    db: Session,
    organization: Organization,
    run: FlowRun,
    approved: bool,
    user: Optional[User] = None,
) -> FlowRun:
    """Resume from the approval checkpoint and publish (or reject) the draft."""
    if run.status not in ("awaiting_approval", "approved", "rejected"):
        raise RuntimeError(f"Cannot resume a run in status '{run.status}'")
    if run.flow_key != "ticket":
        raise RuntimeError("This resume endpoint only applies to ticket flows")

    ticket = db.get(Ticket, run.input_data.get("ticket_id"))
    if ticket is None or ticket.organization_id != organization.id:
        raise RuntimeError("Associated ticket was deleted")

    run.checkpoint["approved"] = approved
    run.checkpoint["reviewed_by"] = user.id if user else None
    run.checkpoint = {**run.checkpoint}

    if not approved:
        runner.set_status(db, run, "rejected")
        from ..models import TicketMessage

        db.add(
            TicketMessage(
                ticket_id=ticket.id,
                sender="system",
                content="An AI draft was reviewed and rejected by a teammate. The ticket stays open for manual handling.",
                meta_json={"flow_run_id": run.id},
            )
        )
        audit.log_activity(
            db,
            organization_id=organization.id,
            user_id=user.id if user else None,
            action="flow.ticket.draft_rejected",
            entity_type="flow_run",
            entity_id=run.id,
            metadata={"ticket_id": ticket.id},
        )
        db.commit()
        db.refresh(run)
        return run

    runner.set_status(db, run, "approved")
    _publish(db, organization, run, ticket)
    runner.set_status(db, run, "completed")
    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id if user else None,
        action="flow.ticket.approved_and_published",
        entity_type="flow_run",
        entity_id=run.id,
        metadata={"ticket_id": ticket.id},
    )
    db.commit()
    db.refresh(run)
    return run
