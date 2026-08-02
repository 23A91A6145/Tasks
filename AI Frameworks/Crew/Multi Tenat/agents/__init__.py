import sys
from pathlib import Path

# Bridge to apps/backend/app/agents
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents import (
    handle_ticket,
)
from app.agents.engine import HandleResult, resolve_engine_name
from app.agents import crew_support, direct_engine, fallback_engine

__all__ = [
    "handle_ticket",
    "HandleResult",
    "resolve_engine_name",
    "crew_support",
    "direct_engine",
    "fallback_engine",
]
