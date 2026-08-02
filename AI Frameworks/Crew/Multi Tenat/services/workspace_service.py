"""Workspace / multi-tenancy business logic."""

import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.permissions import ROLE_ADMIN, ROLE_OWNER, ROLE_USER, VALID_ROLES, can
from ..models import ActivityLog, Membership, Organization, User
from ..schemas.auth import UserOut
from ..schemas.workspace import (
    ActivityOut,
    DailyCount,
    MemberInvite,
    MemberOut,
    MemberRoleUpdate,
    WorkspaceCreate,
    WorkspaceOut,
    WorkspaceStats,
    WorkspaceUpdate,
)
from ..services import audit


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "workspace"


def unique_slug(db: Session, name: str) -> str:
    base = slugify(name)
    slug = base
    counter = 2
    while db.execute(select(Organization).where(Organization.slug == slug)).scalar_one_or_none():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def _workspace_out(db: Session, org: Organization, user: User) -> WorkspaceOut:
    member_count = db.execute(
        select(func.count(Membership.id)).where(Membership.organization_id == org.id)
    ).scalar_one()
    your_role = db.execute(
        select(Membership.role).where(
            Membership.organization_id == org.id, Membership.user_id == user.id
        )
    ).scalar_one_or_none()
    return WorkspaceOut(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        plan=org.plan,
        created_at=org.created_at,
        member_count=member_count,
        your_role=your_role or ROLE_USER,
    )


def create_workspace(db: Session, user: User, data: WorkspaceCreate) -> WorkspaceOut:
    if data.slug:
        slug = data.slug
        if db.execute(select(Organization).where(Organization.slug == slug)).scalar_one_or_none():
            raise HTTPException(status_code=409, detail="That workspace address is already taken")
    else:
        slug = unique_slug(db, data.name)

    org = Organization(name=data.name.strip(), slug=slug)
    db.add(org)
    db.flush()
    db.add(Membership(organization_id=org.id, user_id=user.id, role=ROLE_OWNER))
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=user.id,
        action="workspace.created",
        entity_type="organization",
        entity_id=org.id,
        metadata={"name": org.name},
    )
    db.commit()
    db.refresh(org)
    return _workspace_out(db, org, user)


def list_workspaces(db: Session, user: User) -> list[WorkspaceOut]:
    orgs = (
        db.execute(
            select(Organization)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(Membership.user_id == user.id, Membership.status == "active")
            .order_by(Organization.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_workspace_out(db, org, user) for org in orgs]


def get_workspace(db: Session, user: User, slug: str) -> WorkspaceOut:
    org = _require_membership(db, user, slug).organization
    return _workspace_out(db, org, user)


def update_workspace(db: Session, user: User, slug: str, data: WorkspaceUpdate) -> WorkspaceOut:
    membership = _require_membership(db, user, slug)
    if not can(membership.role, ROLE_ADMIN):
        raise HTTPException(status_code=403, detail="Only admins can update workspace settings")

    org = membership.organization
    if data.name is not None:
        org.name = data.name.strip()
    if data.description is not None:
        org.description = data.description.strip() or None
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=user.id,
        action="workspace.updated",
        entity_type="organization",
        entity_id=org.id,
    )
    db.commit()
    db.refresh(org)
    return _workspace_out(db, org, user)


def delete_workspace(db: Session, user: User, slug: str) -> None:
    membership = _require_membership(db, user, slug)
    if not can(membership.role, ROLE_OWNER):
        raise HTTPException(status_code=403, detail="Only the owner can delete a workspace")

    org = membership.organization
    org_id = org.id

    audit.log_activity(
        db,
        organization_id=org_id,
        user_id=user.id,
        action="workspace.deleted",
        entity_type="organization",
        entity_id=org_id,
        metadata={"name": org.name, "plan": org.plan},
    )
    db.commit()

    # Explicit tenant-wide cleanup so nothing is orphaned (SQLite keeps foreign
    # keys off; Postgres would otherwise raise an FK integrity error).
    from sqlalchemy import delete as sa_delete

    from ..core.config import settings
    from ..models import (
        AgentConfig,
        FlowRun,
        Job,
        KnowledgeDocument,
        KnowledgeTag,
        Ticket,
        TicketMessage,
        UsageRecord,
    )

    db.execute(sa_delete(TicketMessage).where(TicketMessage.ticket_id.in_(
        select(Ticket.id).where(Ticket.organization_id == org_id)
    )).execution_options(synchronize_session=False))
    db.execute(sa_delete(Ticket).where(Ticket.organization_id == org_id).execution_options(synchronize_session=False))
    db.execute(sa_delete(FlowRun).where(FlowRun.organization_id == org_id).execution_options(synchronize_session=False))
    db.execute(sa_delete(AgentConfig).where(AgentConfig.organization_id == org_id).execution_options(synchronize_session=False))
    db.execute(sa_delete(Job).where(Job.organization_id == org_id).execution_options(synchronize_session=False))
    db.execute(sa_delete(UsageRecord).where(UsageRecord.organization_id == org_id).execution_options(synchronize_session=False))
    db.execute(sa_delete(KnowledgeTag).where(KnowledgeTag.organization_id == org_id).execution_options(synchronize_session=False))
    db.execute(sa_delete(KnowledgeDocument).where(KnowledgeDocument.organization_id == org_id).execution_options(synchronize_session=False))

    db.delete(org)  # memberships + activity logs cascade
    db.commit()

    # Drop the tenant vector namespace and stored document files.
    try:
        from ..services.vector import get_vector_store

        get_vector_store().delete_namespace(org_id)
    except Exception:  # pragma: no cover — never let cleanup break the delete
        pass
    import os
    import shutil

    doc_dir = os.path.join(settings.STORAGE_DIR, "documents", org_id)
    shutil.rmtree(doc_dir, ignore_errors=True)


def list_members(db: Session, user: User, slug: str) -> list[MemberOut]:
    org = _require_membership(db, user, slug).organization
    rows = db.execute(
        select(Membership, User)
        .join(User, Membership.user_id == User.id)
        .where(Membership.organization_id == org.id)
        .order_by(Membership.created_at.asc())
    ).all()
    return [
        MemberOut(
            user=UserOut.model_validate(member_user),
            role=mem.role,
            status=mem.status,
            joined_at=mem.created_at,
        )
        for mem, member_user in rows
    ]


def invite_member(db: Session, user: User, slug: str, data: MemberInvite) -> MemberOut:
    membership = _require_membership(db, user, slug)
    if not can(membership.role, ROLE_ADMIN):
        raise HTTPException(status_code=403, detail="Only admins can invite members")
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=422, detail=f"Invalid role. Choose from {list(VALID_ROLES)}")

    org = membership.organization
    from .plans import check_seat_quota

    check_seat_quota(db, org)
    target = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if not target:
        raise HTTPException(
            status_code=404,
            detail="That person is not registered yet. They must create an account first.",
        )

    existing = db.execute(
        select(Membership).where(
            Membership.organization_id == org.id, Membership.user_id == target.id
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="That person is already a member")

    new_membership = Membership(organization_id=org.id, user_id=target.id, role=data.role)
    db.add(new_membership)
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=user.id,
        action="member.invited",
        entity_type="user",
        entity_id=target.id,
        metadata={"email": target.email, "role": data.role},
    )
    db.commit()
    db.refresh(new_membership)
    return MemberOut(
        user=UserOut.model_validate(target),
        role=data.role,
        status="active",
        joined_at=new_membership.created_at,
    )


def change_member_role(
    db: Session, user: User, slug: str, target_user_id: str, data: MemberRoleUpdate
) -> MemberOut:
    membership = _require_membership(db, user, slug)
    if not can(membership.role, ROLE_ADMIN):
        raise HTTPException(status_code=403, detail="Only admins can change member roles")
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=422, detail=f"Invalid role. Choose from {list(VALID_ROLES)}")

    org = membership.organization
    target = db.execute(
        select(Membership).where(
            Membership.organization_id == org.id, Membership.user_id == target_user_id
        )
    ).scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found in this workspace")

    if target.role == ROLE_OWNER:
        owner_count = db.execute(
            select(func.count(Membership.id)).where(
                Membership.organization_id == org.id, Membership.role == ROLE_OWNER
            )
        ).scalar_one()
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="A workspace must keep at least one owner")

    target.role = data.role
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=user.id,
        action="member.role_changed",
        entity_type="user",
        entity_id=target_user_id,
        metadata={"role": data.role},
    )
    db.commit()
    db.refresh(target)
    return MemberOut(
        user=UserOut.model_validate(db.get(User, target_user_id)),
        role=target.role,
        status=target.status,
        joined_at=target.created_at,
    )


def remove_member(db: Session, user: User, slug: str, target_user_id: str) -> None:
    membership = _require_membership(db, user, slug)
    if not can(membership.role, ROLE_ADMIN):
        raise HTTPException(status_code=403, detail="Only admins can remove members")

    org = membership.organization
    target = db.execute(
        select(Membership).where(
            Membership.organization_id == org.id, Membership.user_id == target_user_id
        )
    ).scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found in this workspace")

    if target.user_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself")
    if target.role == ROLE_OWNER:
        owner_count = db.execute(
            select(func.count(Membership.id)).where(
                Membership.organization_id == org.id, Membership.role == ROLE_OWNER
            )
        ).scalar_one()
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="A workspace must keep at least one owner")

    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=user.id,
        action="member.removed",
        entity_type="user",
        entity_id=target_user_id,
        metadata={"email": target.user.email},
    )
    db.delete(target)
    db.commit()


def activity_feed(db: Session, user: User, slug: str, limit: int = 20) -> list[ActivityOut]:
    org = _require_membership(db, user, slug).organization
    rows = db.execute(
        select(ActivityLog, User)
        .outerjoin(User, ActivityLog.user_id == User.id)
        .where(ActivityLog.organization_id == org.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    ).all()
    return [
        ActivityOut(
            id=entry.id,
            action=entry.action,
            entity_type=entry.entity_type,
            metadata_json=entry.metadata_json,
            created_at=entry.created_at,
            actor_name=actor.full_name if actor else None,
        )
        for entry, actor in rows
    ]


def workspace_stats(db: Session, user: User, slug: str) -> WorkspaceStats:
    org = _require_membership(db, user, slug).organization
    member_count = db.execute(
        select(func.count(Membership.id)).where(Membership.organization_id == org.id)
    ).scalar_one()
    total_activity = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.organization_id == org.id)
    ).scalar_one()

    days = {
        (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d"): 0
        for i in range(6, -1, -1)
    }
    since = datetime.now(timezone.utc) - timedelta(days=7)
    rows = db.execute(
        select(
            func.date(ActivityLog.created_at).label("day"),
            func.count(ActivityLog.id),
        )
        .where(ActivityLog.organization_id == org.id, ActivityLog.created_at >= since)
        .group_by("day")
    ).all()
    for day, count in rows:
        if day in days:
            days[day] = count

    your_role = db.execute(
        select(Membership.role).where(
            Membership.organization_id == org.id, Membership.user_id == user.id
        )
    ).scalar_one_or_none()

    return WorkspaceStats(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        your_role=your_role or ROLE_USER,
        member_count=member_count,
        total_activity=total_activity,
        activity_7d=[DailyCount(date=day, count=count) for day, count in days.items()],
    )


def _require_membership(db: Session, user: User, slug: str) -> Membership:
    membership = db.execute(
        select(Membership)
        .join(Organization, Membership.organization_id == Organization.id)
        .where(Organization.slug == slug, Membership.user_id == user.id)
    ).scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")
    return membership
