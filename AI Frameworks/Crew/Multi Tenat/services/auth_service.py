"""Authentication business logic."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from ..models import Membership, Organization, User
from ..schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MembershipOut,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)
from ..services import audit, email
from ..core.permissions import ROLE_OWNER
from .workspace_service import unique_slug


def _memberships_out(db: Session, user_id: str) -> list[MembershipOut]:
    rows = db.execute(
        select(Membership, Organization)
        .join(Organization, Membership.organization_id == Organization.id)
        .where(Membership.user_id == user_id, Membership.status == "active")
    ).all()
    return [
        MembershipOut(
            organization_id=org.id,
            organization_name=org.name,
            organization_slug=org.slug,
            role=mem.role,
            status=mem.status,
        )
        for mem, org in rows
    ]


def _token_response(db: Session, user: User, include_refresh: bool = True) -> TokenResponse:
    refresh = create_refresh_token(user.id) if include_refresh else None
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=refresh,
        user=UserOut.model_validate(user),
        memberships=_memberships_out(db, user.id),
    )


def register(db: Session, data: RegisterRequest) -> TokenResponse:
    existing = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name.strip(),
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    audit.log_activity(
        db,
        organization_id=None,
        user_id=user.id,
        action="auth.registered",
        entity_type="user",
        entity_id=user.id,
        metadata={"email": user.email},
    )

    if data.workspace_name:
        org = Organization(name=data.workspace_name.strip(), slug=unique_slug(db, data.workspace_name))
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
    db.refresh(user)
    return _token_response(db, user)


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    audit.log_activity(
        db,
        organization_id=None,
        user_id=user.id,
        action="auth.login",
        entity_type="user",
        entity_id=user.id,
    )
    db.commit()
    db.refresh(user)
    return _token_response(db, user)


def demo_login(db: Session) -> TokenResponse:
    """One-click demo access — provisions the shared demo workspace on demand."""
    from ..services.demo import ensure_demo

    user = ensure_demo(db)
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(db, user)


def refresh_access(db: Session, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except Exception as exc:  # PyJWTError
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = db.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return _token_response(db, user, include_refresh=True)


def request_password_reset(db: Session, data: ForgotPasswordRequest) -> dict:
    """Issue a single-use reset token and 'send' the reset email.

    The response is deliberately identical whether or not the account exists,
    so the endpoint cannot be used to enumerate registered emails.
    """
    user = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if user is None or not user.is_active:
        return {
            "message": "If an account exists for that email, a password reset link has been sent.",
        }

    token = create_password_reset_token(user.id)
    user.password_reset_token = token
    user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.add(user)
    db.commit()

    audit.log_activity(
        db,
        organization_id=None,
        user_id=user.id,
        action="auth.password_reset_requested",
        entity_type="user",
        entity_id=user.id,
    )

    reset_url = email.send_password_reset(user.email, token)
    message = "If an account exists for that email, a password reset link has been sent."
    if reset_url:
        message = (
            f"{message} (Development mode: EMAIL_MODE=log, so the link is shown here "
            "instead of being emailed.)"
        )
    result: dict = {"message": message}
    if reset_url:
        result["reset_link"] = reset_url
    return result


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def reset_password(db: Session, data: ResetPasswordRequest) -> dict:
    """Validate the reset token and set a new password (single use)."""
    try:
        payload = decode_token(data.token)
    except Exception as exc:  # PyJWTError
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired") from exc
    if payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired")

    user = db.get(User, payload.get("sub"))
    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired")
    if user.password_reset_token != data.token:
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired")
    expires_at = _as_utc(user.password_reset_expires_at)
    if expires_at is None or expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset link has expired")

    user.password_hash = hash_password(data.password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    db.add(user)
    db.commit()

    audit.log_activity(
        db,
        organization_id=None,
        user_id=user.id,
        action="auth.password_reset_completed",
        entity_type="user",
        entity_id=user.id,
    )
    return {"message": "Password updated. You can now sign in with your new password."}
