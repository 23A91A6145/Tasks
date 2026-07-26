import uuid
import threading
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"


class StepResult(BaseModel):
    step: str
    result: str
    status: str = "completed"
    error: Optional[str] = None


class Job(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    task: str
    status: JobStatus = JobStatus.PENDING
    plan: list[str] = []
    results: list[StepResult] = []
    current_step: Optional[str] = None
    error: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class JobStore:
    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, task: str) -> Job:
        with self._lock:
            job = Job(task=task)
            self._jobs[job.job_id] = job
            return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs) -> Optional[Job]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            job.updated_at = datetime.now().isoformat()
            return job

    def append_result(self, job_id: str, result: StepResult) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.results.append(result)
                job.updated_at = datetime.now().isoformat()

    def all(self) -> list[Job]:
        with self._lock:
            return list(self._jobs.values())

    def logs(self, job_id: str) -> Optional[list[dict]]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            return [
                {
                    "step": r.step,
                    "result": r.result,
                    "status": r.status,
                    "error": r.error,
                }
                for r in job.results
            ]


store = JobStore()
