"""Ticket business logic."""

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Organization, Ticket, TicketMessage, User
from ..schemas.tickets import TicketCreate, TicketDetailOut, TicketMessageOut, TicketOut
from ..services import audit


def _message_out(msg: TicketMessage) -> TicketMessageOut:
    sender_name = msg.sender_user.full_name if msg.sender_user else None
    return TicketMessageOut(
        id=msg.id,
        ticket_id=msg.ticket_id,
        sender=msg.sender,
        sender_user_id=msg.sender_user_id,
        sender_name=sender_name,
        content=msg.content,
        meta_json=msg.meta_json,
        created_at=msg.created_at,
    )


def list_tickets(
    db: Session, organization_id: str, status: str | None = None, limit: int = 50
) -> list[TicketOut]:
    stmt = (
        select(Ticket)
        .where(Ticket.organization_id == organization_id)
        .order_by(Ticket.updated_at.desc())
        .limit(min(limit, 100))
    )
    if status:
        stmt = stmt.where(Ticket.status == status)
    tickets = db.execute(stmt).scalars().all()
    return [_ticket_out(db, ticket) for ticket in tickets]


def get_ticket(db: Session, organization_id: str, ticket_id: str) -> TicketDetailOut:
    ticket = _require(db, organization_id, ticket_id)
    return _detail_out(db, ticket)


def create_ticket(
    db: Session, organization_id: str, user: User, data: TicketCreate
) -> TicketDetailOut:
    ticket = Ticket(
        organization_id=organization_id,
        subject=data.subject.strip(),
        body=data.body.strip(),
        priority=data.priority,
        created_by_id=user.id,
    )
    db.add(ticket)
    db.flush()
    db.add(
        TicketMessage(
            ticket_id=ticket.id,
            sender="user",
            sender_user_id=user.id,
            content=data.body.strip(),
            meta_json={"source": "portal"},
        )
    )
    audit.log_activity(
        db,
        organization_id=organization_id,
        user_id=user.id,
        action="ticket.created",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata={"subject": ticket.subject},
    )
    db.commit()
    db.refresh(ticket)
    return _detail_out(db, ticket)


def add_message(
    db: Session, organization_id: str, ticket_id: str, user: User, content: str
) -> TicketMessageOut:
    ticket = _require(db, organization_id, ticket_id)
    if ticket.status in ("resolved", "closed"):
        ticket.status = "open"
    message = TicketMessage(
        ticket_id=ticket.id,
        sender="user",
        sender_user_id=user.id,
        content=content.strip(),
    )
    db.add(message)
    audit.log_activity(
        db,
        organization_id=organization_id,
        user_id=user.id,
        action="ticket.message_added",
        entity_type="ticket",
        entity_id=ticket.id,
    )
    db.commit()
    db.refresh(message)
    return _message_out(message)


def _ticket_out(db: Session, ticket: Ticket) -> TicketOut:
    message_count = db.execute(
        select(func.count(TicketMessage.id)).where(TicketMessage.ticket_id == ticket.id)
    ).scalar_one()
    created_by_name = ticket.created_by.full_name if ticket.created_by else None
    return TicketOut(
        id=ticket.id,
        subject=ticket.subject,
        body=ticket.body,
        status=ticket.status,
        priority=ticket.priority,
        classification=ticket.classification,
        ai_summary=ticket.ai_summary,
        created_by_id=ticket.created_by_id,
        created_by_name=created_by_name,
        assigned_agent_id=ticket.assigned_agent_id,
        resolved_at=ticket.resolved_at,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        message_count=message_count,
    )


def _detail_out(db: Session, ticket: Ticket) -> TicketDetailOut:
    messages = (
        db.execute(
            select(TicketMessage)
            .options()
            .where(TicketMessage.ticket_id == ticket.id)
            .order_by(TicketMessage.created_at.asc())
        )
        .scalars()
        .all()
    )
    base = _ticket_out(db, ticket)
    return TicketDetailOut(**base.model_dump(), messages=[_message_out(m) for m in messages])


def _require(db: Session, organization_id: str, ticket_id: str) -> Ticket:
    ticket = db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == organization_id,
        )
    ).scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found in this workspace")
    return ticket
