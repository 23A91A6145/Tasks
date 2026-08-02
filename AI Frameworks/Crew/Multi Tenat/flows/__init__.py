import sys
from pathlib import Path

# Bridge to apps/backend/app/flows
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.flows import escalation_flow, feedback_flow, runner, ticket_flow
from app.flows.runner import create_run, save, get_run, list_runs, set_status, set_step, set_output, FlowRun
from app.flows.ticket_flow import run_ticket_flow, resume_ticket_flow
from app.flows.escalation_flow import run_escalation_flow
from app.flows.feedback_flow import run_feedback_flow

__all__ = [
    "escalation_flow",
    "feedback_flow",
    "runner",
    "ticket_flow",
    "create_run",
    "save",
    "get_run",
    "list_runs",
    "set_status",
    "set_step",
    "set_output",
    "FlowRun",
    "run_ticket_flow",
    "resume_ticket_flow",
    "run_escalation_flow",
    "run_feedback_flow",
]
