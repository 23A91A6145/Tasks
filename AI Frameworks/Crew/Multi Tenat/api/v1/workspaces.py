import secrets

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, require_admin, require_role, get_workspace_membership
from ...core.database import get_db
from ...core.permissions import ROLE_ADMIN, ROLE_OWNER
from ...models import Membership, Organization, User
from ...schemas.workspace import (
    ActivityOut,
    MemberInvite,
    MemberOut,
    MemberRoleUpdate,
    WorkspaceCreate,
    WorkspaceOut,
    WorkspaceStats,
    WorkspaceUpdate,
)
from ...services import webhooks, workspace_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceOut])
def list_workspaces(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[WorkspaceOut]:
    return workspace_service.list_workspaces(db, user)


@router.post("", response_model=WorkspaceOut, status_code=201)
def create_workspace(
    data: WorkspaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceOut:
    return workspace_service.create_workspace(db, user, data)


@router.get("/{slug}", response_model=WorkspaceOut)
def get_workspace(
    slug: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceOut:
    return workspace_service.get_workspace(db, user, slug)


@router.patch("/{slug}", response_model=WorkspaceOut)
def update_workspace(
    slug: str,
    data: WorkspaceUpdate,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> WorkspaceOut:
    return workspace_service.update_workspace(db, membership.user, slug, data)


@router.delete("/{slug}", status_code=204)
def delete_workspace(
    slug: str,
    membership: Membership = Depends(require_role(ROLE_OWNER)),
    db: Session = Depends(get_db),
) -> Response:
    workspace_service.delete_workspace(db, membership.user, slug)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{slug}/members", response_model=list[MemberOut])
def list_members(
    slug: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MemberOut]:
    return workspace_service.list_members(db, user, slug)


@router.post("/{slug}/members", response_model=MemberOut, status_code=201)
def invite_member(
    slug: str,
    data: MemberInvite,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> MemberOut:
    return workspace_service.invite_member(db, membership.user, slug, data)


@router.patch("/{slug}/members/{user_id}", response_model=MemberOut)
def change_member_role(
    slug: str,
    user_id: str,
    data: MemberRoleUpdate,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> MemberOut:
    return workspace_service.change_member_role(db, membership.user, slug, user_id, data)


@router.delete("/{slug}/members/{user_id}", status_code=204)
def remove_member(
    slug: str,
    user_id: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Response:
    workspace_service.remove_member(db, membership.user, slug, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{slug}/activity", response_model=list[ActivityOut])
def activity_feed(
    slug: str,
    limit: int = 20,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> list[ActivityOut]:
    return workspace_service.activity_feed(db, membership.user, slug, limit=min(limit, 100))


@router.get("/{slug}/stats", response_model=WorkspaceStats)
def stats(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> WorkspaceStats:
    return workspace_service.workspace_stats(db, membership.user, slug)


# ─────────────────────────── AI widget (end-user chat) ───────────────────────────


@router.get("/{slug}/widget")
def widget_status(
    slug: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    settings = org.settings or {}
    return {
        "enabled": bool(settings.get("widget_enabled")),
        "token": settings.get("widget_token", ""),
        "endpoint": f"/api/v1/public/{org.slug}/chat",
        "example_curl": (
            f"curl -s http://localhost:8000/api/v1/public/{org.slug}/chat \\\n"
            f"  -H 'Content-Type: application/json' \\\n"
            f"  -H 'X-Widget-Token: {settings.get('widget_token', '')}' \\\n"
            f"  -d '{{\"message\": \"How do I reset my password?\"}}'"
        ),
    }


@router.get("/{slug}/widget/config")
def widget_config(
    slug: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    settings = org.settings or {}
    return {
        "widget_enabled": bool(settings.get("widget_enabled")),
        "widget_token": settings.get("widget_token", ""),
        "widget_url": f"/api/v1/public/{org.slug}/chat",
    }


@router.post("/{slug}/widget/enable")
def widget_enable(
    slug: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    from ...services import audit

    org = db.get(Organization, membership.organization_id)
    settings = dict(org.settings or {})
    settings["widget_enabled"] = True
    if not settings.get("widget_token"):
        settings["widget_token"] = secrets.token_urlsafe(32)
    org.settings = settings
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=membership.user_id,
        action="widget.enabled",
        entity_type="organization",
        entity_id=org.id,
    )
    db.commit()
    db.refresh(org)
    return {"enabled": True, "token": settings["widget_token"]}


@router.post("/{slug}/widget/rotate")
def widget_rotate(
    slug: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    from ...services import audit

    org = db.get(Organization, membership.organization_id)
    settings = dict(org.settings or {})
    settings["widget_token"] = secrets.token_urlsafe(32)
    org.settings = settings
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=membership.user_id,
        action="widget.token_rotated",
        entity_type="organization",
        entity_id=org.id,
    )
    db.commit()
    db.refresh(org)
    return {"enabled": bool(settings.get("widget_enabled")), "token": settings["widget_token"]}


@router.post("/{slug}/widget/disable")
def widget_disable(
    slug: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    from ...services import audit

    org = db.get(Organization, membership.organization_id)
    settings = dict(org.settings or {})
    settings["widget_enabled"] = False
    org.settings = settings
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=membership.user_id,
        action="widget.disabled",
        entity_type="organization",
        entity_id=org.id,
    )
    db.commit()
    db.refresh(org)
    return {"enabled": False}


# ─────────────────────────── Outbound webhooks ───────────────────────────


class WebhookUpdate(BaseModel):
    url: str = Field(min_length=5, max_length=2000)
    secret: str = Field(default="", max_length=200)
    events: list[str] = Field(
        default_factory=lambda: ["ticket.created", "ticket.ai_handled", "flow.approved"],
        max_length=20,
    )


@router.get("/{slug}/webhooks")
def webhook_get(
    slug: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    return webhooks.get_config(org)


@router.post("/{slug}/webhooks")
def webhook_set(
    slug: str,
    data: WebhookUpdate,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    from ...services import audit

    org = db.get(Organization, membership.organization_id)
    result = webhooks.set_config(db, org, url=data.url, secret=data.secret, events=data.events)
    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=membership.user_id,
        action="webhook.configured",
        entity_type="organization",
        entity_id=org.id,
        metadata={"url": result["webhook_url"], "events": result["webhook_events"]},
    )
    return result


@router.post("/{slug}/webhooks/test")
def webhook_test(
    slug: str,
    membership: Membership = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    org = db.get(Organization, membership.organization_id)
    return webhooks.deliver(
        org,
        "test.ping",
        {"message": "Hello from TenantDesk AI — your webhook is configured correctly."},
    )
