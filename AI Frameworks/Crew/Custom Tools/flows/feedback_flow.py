"""Feedback flow — records satisfaction ratings on a resolved ticket.

start → record → done
"""

from typing import Optional

from sqlalchemy.orm import Session

from ..models import FlowRun, Organization, Ticket, User
from ..services import audit
from . import runner


def run_feedback_flow(
    db: Session,
    organization: Organization,
    ticket: Ticket,
    rating: int,
    comment: str = "",
    user: Optional[User] = None,
) -> FlowRun:
    rating = max(1, min(5, rating))
    run = runner.create_run(
        db,
        organization,
        "feedback",
        {"ticket_id": ticket.id, "rating": rating, "comment": comment},
        user=user,
    )
    from ..services import usage

    usage.track(
        db,
        organization_id=organization.id,
        user_id=user.id if user else None,
        kind="flow",
        units=1,
        meta={"action": "feedback.record", "rating": rating},
    )
    runner.set_step(db, run, "record")

    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id if user else None,
        action="feedback.recorded",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata={"flow_run": run.id, "rating": rating, "comment": comment},
    )
    runner.set_output(db, run, ticket_id=ticket.id, rating=rating, comment=comment)
    runner.set_status(db, run, "completed")
    db.commit()
    db.refresh(run)
    return run
