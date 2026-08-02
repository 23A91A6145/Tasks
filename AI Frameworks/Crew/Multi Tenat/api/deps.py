"""Shared FastAPI dependencies: auth, tenancy and RBAC."""

from typing import Callable

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.permissions import ROLE_ADMIN, can
from ..core.security import decode_token
from ..models import Membership, Organization, User

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = db.get(User, payload.get("sub"))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def get_current_super_admin(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin access required")
    return user


def get_workspace_membership(
    slug: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Membership:
    membership = (
        db.query(Membership)
        .join(Organization, Membership.organization_id == Organization.id)
        .filter(Organization.slug == slug, Membership.user_id == user.id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")
    return membership


def require_role(min_role: str) -> Callable:
    """Dependency factory: returns a dependency that enforces a minimum role."""

    def _dependency(
        membership: Membership = Depends(get_workspace_membership),
    ) -> Membership:
        if not can(membership.role, min_role):
            raise HTTPException(
                status_code=403,
                detail=f"Requires role '{min_role}' or higher in this workspace",
            )
        return membership

    return _dependency


require_admin = require_role(ROLE_ADMIN)
