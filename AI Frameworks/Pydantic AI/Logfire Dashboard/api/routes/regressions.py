"""Regression, comparison, trace inspection, and feedback ingestion API endpoints."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from evals.compare import compare_experiments, load_experiment_report, get_available_reports
from evals.production_feedback import ingest_production_incident, evaluate_ingested_incident

router = APIRouter(prefix="/api", tags=["regressions"])


class CompareRequest(BaseModel):
    """Payload to compare two experiment runs."""
    baseline_id: str | None = None
    current_id: str = "latest"


class IngestIncidentRequest(BaseModel):
    """Payload to ingest a production failure."""
    incident_id: str = Field(description="Unique incident identifier (e.g. PROD-1024)")
    prompt: str = Field(description="User input prompt that triggered failure")
    bad_output: str = Field(description="Bad/failing response produced by agent")
    expected_output: str = Field(description="Expected ground truth response")
    category: str = "production_failure"
    risk: str = "medium"
    tags: list[str] = Field(default_factory=lambda: ["production_incident"])


@router.post("/experiments/compare")
def compare_runs(req: CompareRequest) -> dict[str, Any]:
    """Compare two experiments side-by-side."""
    reports = get_available_reports()
    if not reports:
        raise HTTPException(status_code=400, detail="No historical reports available to compare.")

    current_data = load_experiment_report(req.current_id)

    if req.baseline_id:
        baseline_data = load_experiment_report(req.baseline_id)
    else:
        baseline_data = load_experiment_report(reports[1]) if len(reports) >= 2 else current_data

    return compare_experiments(baseline_data, current_data)


@router.post("/feedback/ingest")
async def ingest_feedback_incident(req: IngestIncidentRequest) -> dict[str, Any]:
    """Ingest a production failure trace and immediately evaluate against current agent."""
    record = ingest_production_incident(
        incident_id=req.incident_id,
        user_prompt=req.prompt,
        bad_agent_output=req.bad_output,
        expected_ground_truth=req.expected_output,
        category=req.category,
        risk=req.risk,
        tags=req.tags,
    )
    result = await evaluate_ingested_incident(record)
    return {
        "status": "ingested",
        "incident_record": record,
        "evaluation_result": result,
    }


@router.get("/traces/{case_name}")
def get_case_trace(case_name: str, report_id: str = "latest") -> dict[str, Any]:
    """Retrieve execution trace tree and evaluator breakdown for a case."""
    try:
        report = load_experiment_report(report_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

    cases = report.get("cases", [])
    matched = [c for c in cases if case_name.lower() in c.get("case_name", "").lower()]
    if not matched:
        raise HTTPException(status_code=404, detail=f"Case '{case_name}' not found in report.")

    return matched[0]
