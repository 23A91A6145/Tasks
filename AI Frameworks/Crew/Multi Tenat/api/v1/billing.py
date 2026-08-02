from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...api.deps import get_workspace_membership
from ...core.database import get_db
from ...core.permissions import ROLE_OWNER
from ...models import Membership, Organization
from ...services import plans as plans_service

router = APIRouter(prefix="/workspaces/{slug}/billing", tags=["billing"])


class PlanChangeRequest(BaseModel):
    plan: str = Field(min_length=1, max_length=20)


@router.get("/summary")
def billing_summary(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    """Current plan, usage vs limits, and the full plan catalog."""
    org = db.get(Organization, membership.organization_id)
    return plans_service.billing_summary(db, org)


@router.post("/change")
def change_plan(
    slug: str,
    data: PlanChangeRequest,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    """Change the workspace plan (owner only — enforcement is transparent to the app)."""
    if membership.role != ROLE_OWNER:
        raise HTTPException(status_code=403, detail="Only the workspace owner can change the plan")
    org = db.get(Organization, membership.organization_id)
    plans_service.change_plan(db, org, data.plan, by=membership.user_id)
    db.refresh(org)
    return plans_service.billing_summary(db, org)
