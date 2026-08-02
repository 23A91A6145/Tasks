from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, get_workspace_membership, require_role
from ...core.database import get_db
from ...core.permissions import ROLE_AGENT
from ...models import Membership, Organization, Ticket, User
from ...schemas.tickets import (
    MessageCreate,
    TicketCreate,
    TicketDetailOut,
    TicketHandleOut,
    TicketMessageOut,
    TicketOut,
)
from ...services import plans, ticket_service, webhooks

router = APIRouter(prefix="/workspaces/{slug}/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketOut])
def list_tickets(
    slug: str,
    status: str | None = Query(default=None, pattern=r"^(new|open|pending|resolved|closed|escalated)$"),
    limit: int = Query(default=50, ge=1, le=100),
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> list[TicketOut]:
    return ticket_service.list_tickets(db, membership.organization_id, status=status, limit=limit)


@router.post("", response_model=TicketDetailOut, status_code=201)
def create_ticket(
    slug: str,
    data: TicketCreate,
    membership: Membership = Depends(get_workspace_membership),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketDetailOut:
    detail = ticket_service.create_ticket(db, membership.organization_id, user, data)
    org = db.get(Organization, membership.organization_id)
    webhooks.deliver(
        org,
        "ticket.created",
        {
            "id": detail.id,
            "subject": detail.subject,
            "priority": detail.priority,
            "created_by": detail.created_by_name,
        },
    )
    return detail


@router.get("/{ticket_id}", response_model=TicketDetailOut)
def get_ticket(
    slug: str,
    ticket_id: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> TicketDetailOut:
    return ticket_service.get_ticket(db, membership.organization_id, ticket_id)


@router.post("/{ticket_id}/messages", response_model=TicketMessageOut, status_code=201)
def add_message(
    slug: str,
    ticket_id: str,
    data: MessageCreate,
    membership: Membership = Depends(get_workspace_membership),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketMessageOut:
    return ticket_service.add_message(db, membership.organization_id, ticket_id, user, data.content)


@router.post("/{ticket_id}/ai-handle", response_model=TicketHandleOut)
def ai_handle(
    slug: str,
    ticket_id: str,
    require_approval: bool = Query(default=False),
    membership: Membership = Depends(require_role(ROLE_AGENT)),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketHandleOut:
    """Run the checkpointed ticket flow: classify → retrieve → draft → (approval) → publish."""
    organization = db.get(Organization, membership.organization_id)
    plans.check_request_quota(db, organization)
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or ticket.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Ticket not found in this workspace")

    from ...flows import ticket_flow
    from ...schemas.flows import FlowRunOut

    run = ticket_flow.run_ticket_flow(
        db, organization, ticket, user=user, require_approval=require_approval
    )
    checkpoint = run.checkpoint
    ticket = db.get(Ticket, ticket_id)

    result = TicketHandleOut(
        ticket=ticket_service.get_ticket(db, membership.organization_id, ticket_id),
        flow_run=FlowRunOut.model_validate(run).model_dump(),
        draft=checkpoint.get("draft", ""),
        classification=checkpoint.get("classification", "general"),
        priority=checkpoint.get("priority", "medium"),
        escalate=bool(checkpoint.get("escalate", False)),
        engine=checkpoint.get("engine", "fallback"),
        sources=checkpoint.get("sources", []),
        awaiting_approval=run.status == "awaiting_approval",
    )
    webhooks.deliver(
        organization,
        "ticket.ai_handled",
        {
            "ticket_id": ticket.id,
            "classification": result.classification,
            "priority": result.priority,
            "engine": result.engine,
            "awaiting_approval": result.awaiting_approval,
        },
    )
    return result
