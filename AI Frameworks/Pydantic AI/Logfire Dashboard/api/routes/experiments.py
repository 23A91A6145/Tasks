"""Experiments and evaluation execution API endpoints."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from evals.compare import get_available_reports, load_experiment_report
from evals.matrix_runner import run_prompt_model_matrix
from evals.run_eval import run_evaluation_suite

router = APIRouter(prefix="/api", tags=["experiments"])


class RunEvaluationRequest(BaseModel):
    """Payload to trigger an evaluation experiment."""
    dataset_name: str = "support_agent_v2_professional"
    model_name: str = "test"
    min_pass_rate: float = 0.85
    category_filter: str | None = None
    difficulty_filter: str | None = None
    risk_filter: str | None = None
    tag_filter: str | None = None


@router.get("/experiments")
def list_experiments() -> list[dict[str, Any]]:
    """List all historical experiment runs."""
    reports = get_available_reports()
    results = []
    for r in reports:
        try:
            data = load_experiment_report(r)
            m = data.get("metrics", {})
            g = data.get("quality_gate", {})
            results.append({
                "experiment_id": data.get("experiment_id"),
                "timestamp": data.get("timestamp"),
                "dataset_name": data.get("dataset_name"),
                "model_name": data.get("model_name"),
                "pass_rate": m.get("pass_rate", 0.0),
                "composite_score": m.get("avg_composite_score", 0.0),
                "judge_score": m.get("avg_judge_score", 0.0),
                "avg_latency_ms": round(m.get("avg_latency_seconds", 0.0) * 1000, 1),
                "quality_gate_passed": g.get("passed", False),
            })
        except Exception:
            continue
    return results


@router.get("/experiments/{experiment_id}")
def get_experiment_details(experiment_id: str) -> dict[str, Any]:
    """Get full details and case breakdown of a specific experiment."""
    try:
        return load_experiment_report(experiment_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found.")


@router.post("/evals/run")
async def trigger_evaluation(req: RunEvaluationRequest) -> dict[str, Any]:
    """Trigger a live evaluation experiment."""
    report = await run_evaluation_suite(
        dataset_name=req.dataset_name,
        model_name=req.model_name,
        min_pass_rate=req.min_pass_rate,
        category_filter=req.category_filter,
        difficulty_filter=req.difficulty_filter,
        risk_filter=req.risk_filter,
        tag_filter=req.tag_filter,
        save_reports=True,
    )
    return report


@router.get("/matrix")
async def get_matrix_evaluation() -> dict[str, Any]:
    """Execute and return model x prompt comparison matrix."""
    return await run_prompt_model_matrix()
