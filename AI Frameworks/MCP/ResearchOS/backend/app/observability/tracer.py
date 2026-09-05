import time
from datetime import datetime, timezone
from typing import List, Dict, Any
from backend.app.models.schemas import TraceStep, RunTrace

class RunTracer:
    """Records precise execution timeline, step latency, and node transition metrics."""
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.steps: List[TraceStep] = []
        self._start_times: Dict[str, float] = {}

    def start_step(self, step_name: str):
        self._start_times[step_name] = time.time()

    def end_step(self, step_name: str, status: str = "completed", details: Dict[str, Any] = None):
        started_epoch = self._start_times.get(step_name, time.time())
        duration_ms = int((time.time() - started_epoch) * 1000)
        
        self.steps.append(
            TraceStep(
                step_name=step_name,
                status=status,
                started_at=datetime.now(timezone.utc),
                duration_ms=duration_ms,
                details=details or {}
            )
        )

    def to_trace(self, total_sources: int, total_claims: int, total_citations: int) -> RunTrace:
        total_ms = sum(s.duration_ms for s in self.steps)
        return RunTrace(
            run_id=self.run_id,
            steps=self.steps,
            total_duration_ms=total_ms,
            total_sources=total_sources,
            total_claims=total_claims,
            total_citations=total_citations
        )
