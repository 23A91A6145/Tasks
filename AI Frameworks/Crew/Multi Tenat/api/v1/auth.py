from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ...api.deps import get_current_user
from ...core.database import get_db
from ...models import User
from ...schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)
from ...services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Create an account (and optionally a workspace) in one step."""
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.login(db, data)


@router.post("/demo", response_model=TokenResponse)
def demo(db: Session = Depends(get_db)) -> TokenResponse:
    """One-click demo access — no account or setup needed.

    Provisions the shared demo workspace on first call and returns fresh
    tokens, so the entire product is usable immediately on an empty database.
    """
    return auth_service.demo_login(db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.refresh_access(db, data.refresh_token)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """Request a password reset link (safe against account enumeration)."""
    return auth_service.request_password_reset(db, data)


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """Set a new password using the token from the reset email."""
    return auth_service.reset_password(db, data)


@router.post("/logout", status_code=204)
def logout() -> Response:
    """Stateless logout: the client simply discards its tokens."""
    return Response(status_code=204)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
