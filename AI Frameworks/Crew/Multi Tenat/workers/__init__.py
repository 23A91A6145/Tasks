import sys
from pathlib import Path

# Bridge to apps/backend job workers (apps/backend/app/services/jobs.py + scripts.worker)
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.jobs import (
    create_job,
    get_job,
    list_jobs,
    run_job,
    retry_job,
    delete_job,
    queue_and_run,
    run_worker,
)

__all__ = [
    "create_job",
    "get_job",
    "list_jobs",
    "run_job",
    "retry_job",
    "delete_job",
    "queue_and_run",
    "run_worker",
]
