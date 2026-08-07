from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlmodel import Session, select
from apps.api.database import engine
from apps.api.models import AuditLog, User
from jose import jwt
from apps.api.config import settings

class RequestAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Only audit core functional API endpoints under v1 namespace
        if not path.startswith("/api/v1"):
            return await call_next(request)
            
        # Parse user credentials from bearer token if present
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                username = payload.get("sub")
                with Session(engine) as db_session:
                    user = db_session.exec(select(User).where(User.username == username)).first()
                    if user:
                        user_id = user.id
            except Exception:
                pass  # Token is either invalid or expired, proceed safely

        response = await call_next(request)

        # Write API transaction log, omitting credentials for security (no password logs)
        if "/auth/login" not in path and "/auth/register" not in path:
            try:
                ip_addr = request.client.host if request.client else None
                with Session(engine) as db_session:
                    log = AuditLog(
                        event_type="API_REQUEST",
                        user_id=user_id,
                        action=f"HTTP {request.method} {path} processed. Response Status: {response.status_code}",
                        ip_address=ip_addr
                    )
                    db_session.add(log)
                    db_session.commit()
            except Exception as e:
                # Log to stderr to avoid breaking user pipeline on logging crashes
                import sys
                print(f"[AUDIT MIDDLEWARE ERROR]: {e}", file=sys.stderr)

        return response
