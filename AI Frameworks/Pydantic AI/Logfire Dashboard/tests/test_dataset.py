"""Unit tests for evaluation datasets, metadata validation, and slicing analytics."""

from evals.datasets.support_cases import (
    get_support_cases,
    get_support_dataset,
    filter_cases,
    get_dataset_slices,
)
from evals.datasets.edge_cases import get_edge_cases
from evals.datasets.safety_cases import get_safety_cases
from evals.datasets.regression_cases import get_regression_cases


def test_support_dataset_size_and_structure():
    """Verify that dataset contains at least 25-28 comprehensive cases."""
    cases = get_support_cases()
    assert len(cases) >= 25
    assert len(cases) == 28


def test_case_metadata_integrity():
    """Verify every case contains required metadata fields."""
    cases = get_support_cases()
    for case in cases:
        assert case.name, "Case must have a unique non-empty name"
        assert case.inputs is not None, "Case must define inputs"
        assert case.expected_output, "Case must define expected_output"
        assert case.metadata is not None, "Case must contain metadata dictionary"
        assert "category" in case.metadata, "Metadata must contain category"
        assert "difficulty" in case.metadata, "Metadata must contain difficulty"
        assert "risk" in case.metadata, "Metadata must contain risk"


def test_category_distribution():
    """Ensure dataset covers normal, edge, safety, hallucination_trap, and boundary categories."""
    cases = get_support_cases()
    categories = {c.metadata["category"] for c in cases}
    assert "normal" in categories
    assert "edge_case" in categories
    assert "safety" in categories
    assert "hallucination_trap" in categories
    assert "boundary" in categories


def test_metadata_slicing_filtering():
    """Test filtering cases by category, difficulty, risk, and tags."""
    cases = get_support_cases()

    # Category filter
    safety_cases = filter_cases(cases, category="safety")
    assert len(safety_cases) == 3
    assert all(c.metadata["category"] == "safety" for c in safety_cases)

    # Risk filter
    critical_cases = filter_cases(cases, risk="critical")
    assert len(critical_cases) >= 2
    assert all(c.metadata["risk"] == "critical" for c in critical_cases)

    # Difficulty filter
    hard_cases = filter_cases(cases, difficulty="hard")
    assert len(hard_cases) >= 6

    # Tag filter
    refund_cases = filter_cases(cases, tag="refund")
    assert len(refund_cases) >= 4


def test_dataset_slices_summary():
    """Test slice aggregation utility."""
    cases = get_support_cases()
    slices = get_dataset_slices(cases)

    assert "categories" in slices
    assert "difficulties" in slices
    assert "risks" in slices
    assert "tool_requirements" in slices
    assert slices["tool_requirements"]["requires_tool"] > 0
    assert slices["tool_requirements"]["no_tool"] > 0


def test_specialized_datasets():
    """Verify edge, safety, and regression datasets."""
    assert len(get_edge_cases()) >= 3
    assert len(get_safety_cases()) >= 2
    assert len(get_regression_cases()) >= 2
