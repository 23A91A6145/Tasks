import sys
from pathlib import Path

# Bridge to apps/backend/app/tools
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.tools import (
    registry,
    run_calculator,
    run_web_search,
    run_crm_lookup,
    run_send_email,
    run_schedule_calendar,
    run_github_tool,
    get_crewai_tools,
)

__all__ = [
    "registry",
    "run_calculator",
    "run_web_search",
    "run_crm_lookup",
    "run_send_email",
    "run_schedule_calendar",
    "run_github_tool",
    "get_crewai_tools",
]
