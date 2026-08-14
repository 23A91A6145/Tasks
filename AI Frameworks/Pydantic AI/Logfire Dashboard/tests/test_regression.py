"""Unit tests for regression rules and quality gate thresholds."""

from evals.thresholds import QualityThresholds, validate_experiment_thresholds


def test_quality_gate_passes_above_thresholds():
    """Verify that experiment passes when all metrics exceed thresholds."""
    result = validate_experiment_thresholds(
        pass_rate=0.95,
        avg_judge_score=0.90,
        avg_latency=1.2,
        critical_pass_rate=1.0,
    )
    assert result.passed is True
    assert len(result.violations) == 0


def test_quality_gate_fails_on_pass_rate_violation():
    """Verify violation when pass rate drops below minimum."""
    result = validate_experiment_thresholds(
        pass_rate=0.75,  # Below 0.85 default
        avg_judge_score=0.90,
        avg_latency=1.2,
        critical_pass_rate=1.0,
    )
    assert result.passed is False
    assert any("pass rate" in v.lower() for v in result.violations)


def test_regression_detection_from_baseline():
    """Verify regression is flagged when current pass rate drops more than max allowed delta."""
    result = validate_experiment_thresholds(
        pass_rate=0.88,
        avg_judge_score=0.85,
        avg_latency=1.5,
        baseline_pass_rate=0.96,  # 8% drop exceeds 5% max allowed delta
    )
    assert result.passed is False
    assert any("regression detected" in v.lower() for v in result.violations)
