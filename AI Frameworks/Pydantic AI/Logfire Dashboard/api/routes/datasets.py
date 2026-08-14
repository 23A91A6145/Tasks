"""Datasets API endpoints."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException
from evals.datasets import (
    get_support_cases,
    get_edge_cases,
    get_safety_cases,
    get_regression_cases,
    get_production_failure_cases,
    get_dataset_slices,
    filter_cases,
)

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

DATASETS_REGISTRY = {
    "support_agent_v2_professional": get_support_cases,
    "edge_cases": get_edge_cases,
    "safety_cases": get_safety_cases,
    "regression_cases": get_regression_cases,
    "production_failures": get_production_failure_cases,
}


@router.get("")
def list_datasets() -> list[dict[str, Any]]:
    """List all available evaluation datasets and their slice distributions."""
    result = []
    for name, fn in DATASETS_REGISTRY.items():
        cases = fn()
        slices = get_dataset_slices(cases) if name == "support_agent_v2_professional" else {}
        result.append({
            "name": name,
            "total_cases": len(cases),
            "slices": slices,
        })
    return result


@router.get("/{dataset_name}")
def get_dataset(
    dataset_name: str,
    category: str | None = None,
    difficulty: str | None = None,
    risk: str | None = None,
) -> dict[str, Any]:
    """Retrieve test cases in a dataset with optional metadata filtering."""
    if dataset_name not in DATASETS_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found.")

    cases = DATASETS_REGISTRY[dataset_name]()
    if category or difficulty or risk:
        cases = filter_cases(cases, category=category, difficulty=difficulty, risk=risk)

    return {
        "dataset_name": dataset_name,
        "total_cases": len(cases),
        "cases": [
            {
                "name": c.name,
                "inputs": c.inputs,
                "expected_output": c.expected_output,
                "metadata": c.metadata,
            }
            for c in cases
        ],
    }
