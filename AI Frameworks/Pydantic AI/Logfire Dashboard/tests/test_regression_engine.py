"""Unit tests for Multi-Dimensional Regression Engine."""

from evals.regression_engine import RegressionEngine, RegressionRules


def test_regression_engine_passes_on_improvement():
    """Verify engine approves runs with equal or higher pass rate."""
    engine = RegressionEngine()
    baseline = {"metrics": {"pass_rate": 0.90, "avg_latency_seconds": 0.005}, "cases": []}
    current = {"metrics": {"pass_rate": 0.95, "avg_latency_seconds": 0.004}, "cases": []}

    audit = engine.audit_experiment_change(baseline, current)
    assert audit.passed is True
    assert "APPROVED" in audit.verdict


def test_regression_engine_blocks_on_pass_rate_drop():
    """Verify engine flags quality regression when pass rate drops beyond threshold."""
    engine = RegressionEngine(RegressionRules(max_quality_drop_pct=0.03))
    baseline = {"metrics": {"pass_rate": 0.95, "avg_latency_seconds": 0.005}, "cases": []}
    current = {"metrics": {"pass_rate": 0.88, "avg_latency_seconds": 0.005}, "cases": []}

    audit = engine.audit_experiment_change(baseline, current)
    assert audit.passed is False
    assert any(v.dimension == "quality" for v in audit.violations)


def test_regression_engine_zero_tolerance_safety():
    """Verify zero-tolerance trigger on failing safety/critical cases."""
    engine = RegressionEngine()
    baseline = {"metrics": {"pass_rate": 1.0, "avg_latency_seconds": 0.005}, "cases": []}
    current = {
        "metrics": {"pass_rate": 0.95, "avg_latency_seconds": 0.005},
        "cases": [
            {"case_name": "case_23_prompt_injection", "category": "safety", "risk": "critical", "passed": False},
        ],
    }

    audit = engine.audit_experiment_change(baseline, current)
    assert audit.passed is False
    assert any(v.dimension == "safety" and v.severity == "critical" for v in audit.violations)
