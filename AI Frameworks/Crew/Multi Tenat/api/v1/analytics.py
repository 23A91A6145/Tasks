from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...api.deps import get_workspace_membership
from ...core.database import get_db
from ...models import Membership, Organization
from ...services import analytics as analytics_service

router = APIRouter(prefix="/workspaces/{slug}/analytics", tags=["analytics"])


@router.get("/overview")
def analytics_overview(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    """Everything the analytics dashboard needs in one payload."""
    org = db.get(Organization, membership.organization_id)
    return analytics_service.overview(db, org)


@router.get("/summary")
def analytics_summary(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    return analytics_service.summary(db, org)


@router.get("/usage")
def analytics_usage(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    return analytics_service.usage_series(db, org, days=30)


@router.get("/tickets")
def analytics_tickets(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    return analytics_service.ticket_metrics(db, org, days=30)


@router.get("/knowledge")
def analytics_knowledge(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    return analytics_service.knowledge_growth(db, org, days=30)


@router.get("/agents")
def analytics_agents(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    return analytics_service.agent_performance(db, org, days=30)
