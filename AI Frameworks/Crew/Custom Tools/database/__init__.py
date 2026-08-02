import sys
from pathlib import Path

# Bridge to apps/backend database layer (apps/backend/app/core/database.py)
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import Base, engine, SessionLocal, get_db, init_db, utcnow
from app.core.config import settings

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "utcnow",
    "settings",
]
