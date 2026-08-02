from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...api.deps import get_current_super_admin
from ...core.database import get_db
from ...models import ActivityLog, Membership, Organization, User
from ...schemas.auth import UserOut
from ...services.plans import PLANS

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
def overview(
    _: UserOut = Depends(get_current_super_admin), db: Session = Depends(get_db)
) -> dict:
    users = db.execute(select(func.count(User.id))).scalar_one()
    workspaces = db.execute(select(func.count(Organization.id))).scalar_one()
    memberships = db.execute(select(func.count(Membership.id))).scalar_one()
    activities = db.execute(select(func.count(ActivityLog.id))).scalar_one()
    return {
        "users": users,
        "workspaces": workspaces,
        "memberships": memberships,
        "activities": activities,
        "plans": {
            key: {
                "requests_per_month": value["requests_per_month"],
                "knowledge_docs": value["knowledge_docs"],
                "seats": value["seats"],
            }
            for key, value in PLANS.items()
        },
    }


@router.get("/workspaces")
def admin_workspaces(
    _: UserOut = Depends(get_current_super_admin), db: Session = Depends(get_db)
) -> list[dict]:
    rows = db.execute(
        select(
            Organization.id,
            Organization.name,
            Organization.slug,
            Organization.plan,
            Organization.created_at,
            func.count(Membership.id).label("member_count"),
        )
        .outerjoin(Membership, Membership.organization_id == Organization.id)
        .group_by(Organization.id)
        .order_by(Organization.created_at.desc())
    ).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "slug": row.slug,
            "plan": row.plan,
            "created_at": row.created_at,
            "member_count": row.member_count,
        }
        for row in rows
    ]
