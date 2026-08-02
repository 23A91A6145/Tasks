"""Public end-user endpoints — the embeddable AI support widget.

Tenants enable the widget in workspace settings and receive a token. End
users call ``/public/{slug}/chat`` with ``X-Widget-Token`` — no login needed.
Quota + plan limits still apply to the owning tenant.
"""

import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import Organization
from ...services import plans, usage

router = APIRouter(prefix="/public", tags=["public widget"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    engine: str
    classification: str
    priority: str
    sources: list[dict] = []
    tenant: str


def _require_widget(slug: str, token: str | None, db: Session) -> Organization:
    org = db.execute(select(Organization).where(Organization.slug == slug)).scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    settings = org.settings or {}
    if not settings.get("widget_enabled"):
        raise HTTPException(status_code=403, detail="The AI widget is disabled for this workspace")
    if not token or not secrets.compare_digest(str(token), str(settings.get("widget_token", ""))):
        raise HTTPException(status_code=401, detail="Invalid widget token")
    return org


@router.post("/{slug}/chat", response_model=ChatResponse)
def widget_chat(
    slug: str,
    data: ChatRequest,
    x_widget_token: str | None = Header(default=None, alias="X-Widget-Token"),
    db: Session = Depends(get_db),
) -> ChatResponse:
    org = _require_widget(slug, x_widget_token, db)
    plans.check_request_quota(db, org)

    from ...agents import handle_ticket

    result = handle_ticket(db, org, data.message, data.message, top_k=4)
    usage.track(
        db,
        organization_id=org.id,
        kind="flow",
        model=result.engine,
        units=1,
        meta={"action": "widget.chat", "engine": result.engine},
    )
    db.commit()
    return ChatResponse(
        answer=result.draft,
        engine=result.engine,
        classification=result.classification,
        priority=result.priority,
        sources=result.sources,
        tenant=org.name,
    )


@router.post("/{slug}/tickets", status_code=201)
def widget_create_ticket(
    slug: str,
    data: ChatRequest,
    x_widget_token: str | None = Header(default=None, alias="X-Widget-Token"),
    db: Session = Depends(get_db),
) -> dict:
    """End users can escalate to a human ticket from the widget."""
    org = _require_widget(slug, x_widget_token, db)
    plans.check_request_quota(db, org)

    from ...models import Ticket, TicketMessage

    ticket = Ticket(
        organization_id=org.id,
        subject=data.message[:255],
        body=data.message,
        priority="medium",
        status="new",
    )
    db.add(ticket)
    db.flush()
    db.add(TicketMessage(ticket_id=ticket.id, sender="user", content=data.message))
    db.commit()
    return {"ok": True, "ticket_id": ticket.id, "status": "new"}
