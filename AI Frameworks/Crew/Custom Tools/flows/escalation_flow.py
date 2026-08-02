"""Escalation flow — moves a ticket to humans and notifies the team.

start → analyze → notify → done
"""

from typing import Optional

from sqlalchemy.orm import Session

from ..models import FlowRun, Organization, Ticket, User
from ..services import audit
from . import runner


def run_escalation_flow(
    db: Session,
    organization: Organization,
    ticket: Ticket,
    user: Optional[User] = None,
    reason: str = "",
) -> FlowRun:
    run = runner.create_run(
        db,
        organization,
        "escalation",
        {"ticket_id": ticket.id, "reason": reason},
        user=user,
    )
    from ..services import usage

    usage.track(
        db,
        organization_id=organization.id,
        user_id=user.id if user else None,
        kind="flow",
        units=1,
        meta={"action": "ticket.escalate", "reason": reason},
    )
    runner.set_step(db, run, "analyze")

    from ..models import TicketMessage

    ticket.status = "escalated"
    db.add(
        TicketMessage(
            ticket_id=ticket.id,
            sender="system",
            content=f"Ticket escalated to a human teammate. Reason: {reason or 'AI flagged for review'}",
            meta_json={"flow_run_id": run.id},
        )
    )
    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id if user else None,
        action="ticket.escalated",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata={"flow_run": run.id, "reason": reason},
    )

    runner.set_output(db, run, ticket_id=ticket.id, status="escalated")
    runner.set_status(db, run, "completed")
    db.commit()
    db.refresh(run)
    return run
