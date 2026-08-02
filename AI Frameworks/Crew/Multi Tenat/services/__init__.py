import sys
from pathlib import Path

# Bridge to apps/backend/app/services
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services import (
    plans,
    analytics,
    jobs,
    usage,
    audit,
    llm,
    vector,
    embeddings,
    ticket_service,
    workspace_service,
    auth_service,
    knowledge_service,
)

__all__ = [
    "plans",
    "analytics",
    "jobs",
    "usage",
    "audit",
    "llm",
    "vector",
    "embeddings",
    "ticket_service",
    "workspace_service",
    "auth_service",
    "knowledge_service",
]
