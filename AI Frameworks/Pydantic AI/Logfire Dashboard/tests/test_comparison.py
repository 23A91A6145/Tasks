"""Unit tests for experiment comparison engine and regression delta detection."""

from evals.compare import compare_experiments


def test_compare_experiments_identical():
    """Verify comparing identical experiments produces 0 delta and 0 regressions."""
    report_a = {
        "experiment_id": "exp_01",
        "metrics": {"pass_rate": 1.0, "avg_judge_score": 0.95, "avg_latency_seconds": 0.005},
        "cases": [
            {"case_name": "case_01", "passed": True, "composite_score": 1.0},
            {"case_name": "case_02", "passed": True, "composite_score": 1.0},
        ],
    }

    comp = compare_experiments(report_a, report_a)
    assert comp["summary"]["pass_rate"]["delta"] == 0.0
    assert len(comp["flips"]["regressed"]) == 0
    assert comp["summary"]["has_regression"] is False


def test_compare_experiments_detects_regression():
    """Verify regression detection when a previously passing case fails."""
    baseline = {
        "experiment_id": "exp_baseline",
        "metrics": {"pass_rate": 1.0, "avg_judge_score": 0.95, "avg_latency_seconds": 0.005},
        "cases": [
            {"case_name": "case_01", "category": "normal", "passed": True, "composite_score": 1.0},
            {"case_name": "case_02", "category": "safety", "passed": True, "composite_score": 1.0},
        ],
    }

    current = {
        "experiment_id": "exp_regressed",
        "metrics": {"pass_rate": 0.5, "avg_judge_score": 0.70, "avg_latency_seconds": 0.008},
        "cases": [
            {"case_name": "case_01", "category": "normal", "passed": True, "composite_score": 1.0},
            {"case_name": "case_02", "category": "safety", "passed": False, "composite_score": 0.3},
        ],
    }

    comp = compare_experiments(baseline, current)
    assert comp["summary"]["pass_rate"]["delta"] == -0.5
    assert len(comp["flips"]["regressed"]) == 1
    assert comp["flips"]["regressed"][0]["case_name"] == "case_02"
    assert comp["summary"]["has_regression"] is True


def test_compare_experiments_detects_improvement():
    """Verify improvement detection when a previously failing case passes."""
    baseline = {
        "experiment_id": "exp_old",
        "metrics": {"pass_rate": 0.5, "avg_judge_score": 0.60, "avg_latency_seconds": 0.010},
        "cases": [
            {"case_name": "case_01", "category": "normal", "passed": False, "composite_score": 0.4},
        ],
    }

    current = {
        "experiment_id": "exp_fixed",
        "metrics": {"pass_rate": 1.0, "avg_judge_score": 0.95, "avg_latency_seconds": 0.005},
        "cases": [
            {"case_name": "case_01", "category": "normal", "passed": True, "composite_score": 1.0},
        ],
    }

    comp = compare_experiments(baseline, current)
    assert comp["summary"]["pass_rate"]["delta"] == +0.5
    assert len(comp["flips"]["improved"]) == 1
    assert comp["flips"]["improved"][0]["case_name"] == "case_01"
