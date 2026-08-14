"""Unit tests for automated CI Quality Gate."""

from evals.ci_gate import evaluate_ci_quality_gate
from evals.regression_engine import RegressionRules


def test_ci_quality_gate_passes_healthy_report():
    """Verify CI gate passes clean reports."""
    report = {
        "experiment_id": "exp_ci_pass",
        "metrics": {"pass_rate": 1.0, "avg_judge_score": 0.95, "avg_latency_seconds": 0.005},
        "cases": [
            {"case_name": "case_01", "category": "normal", "risk": "low", "passed": True},
        ],
    }
    assert evaluate_ci_quality_gate(report, report, rules=RegressionRules()) is True


def test_ci_quality_gate_blocks_regressed_report():
    """Verify CI gate returns False on severe regression."""
    baseline = {
        "experiment_id": "exp_base",
        "metrics": {"pass_rate": 1.0, "avg_latency_seconds": 0.005},
        "cases": [{"case_name": "case_01", "category": "normal", "risk": "low", "passed": True}],
    }
    regressed = {
        "experiment_id": "exp_bad",
        "metrics": {"pass_rate": 0.50, "avg_latency_seconds": 0.005},
        "cases": [{"case_name": "case_01", "category": "normal", "risk": "low", "passed": False}],
    }
    assert evaluate_ci_quality_gate(regressed, baseline, rules=RegressionRules()) is False
