"""Unit tests for deterministic, tool behavioral, multi-rubric judge, and hybrid scoring engine."""

import pytest
from pydantic_evals import Case
from evals.evaluators.deterministic import DeterministicEvaluator
from evals.evaluators.behavioral import ToolBehaviorEvaluator
from evals.evaluators.performance import PerformanceEvaluator, PerformanceMetrics
from evals.evaluators.llm_judge import CustomLLMJudge, MultiRubricJudgeResult
from evals.evaluators.hybrid import HybridEvaluationEngine


def test_exact_match_evaluator():
    """Test exact string matching."""
    res_pass = DeterministicEvaluator.evaluate_exact_match("Hello World", "hello world", case_sensitive=False)
    assert res_pass.passed is True
    assert res_pass.score == 1.0

    res_fail = DeterministicEvaluator.evaluate_exact_match("Hello World", "Goodbye", case_sensitive=False)
    assert res_fail.passed is False
    assert res_fail.score == 0.0


def test_required_keywords_evaluator():
    """Test required keyword detection."""
    text = "Order A100 is Shipped with tracking TRK-98765."
    res_pass = DeterministicEvaluator.evaluate_required_keywords(text, ["A100", "Shipped", "TRK-98765"])
    assert res_pass.passed is True
    assert res_pass.score == 1.0

    res_partial = DeterministicEvaluator.evaluate_required_keywords(text, ["A100", "Delivered"])
    assert res_partial.passed is False
    assert res_partial.score == 0.5


def test_forbidden_keywords_evaluator():
    """Test forbidden keyword detection for hallucination protection."""
    text = "Order A100 is Shipped with tracking TRK-98765."
    res_pass = DeterministicEvaluator.evaluate_forbidden_keywords(text, ["FEDEX-9999", "Delivered yesterday"])
    assert res_pass.passed is True

    res_fail = DeterministicEvaluator.evaluate_forbidden_keywords("Your tracking is FEDEX-9999", ["FEDEX-9999"])
    assert res_fail.passed is False
    assert res_fail.score == 0.0


def test_latency_evaluator():
    """Test latency threshold verification."""
    res_fast = DeterministicEvaluator.evaluate_latency(0.25, max_duration_seconds=5.0)
    assert res_fast.passed is True

    res_slow = DeterministicEvaluator.evaluate_latency(6.5, max_duration_seconds=5.0)
    assert res_slow.passed is False


def test_tool_behavior_evaluator():
    """Test tool behavioral evaluator."""
    tool_calls = [{"tool": "lookup_order", "args": {"order_id": "A100"}}]

    res_pass = ToolBehaviorEvaluator.evaluate_tool_usage(
        tool_calls=tool_calls,
        expected_tool="lookup_order",
        requires_tool=True,
    )
    assert res_pass.passed is True

    res_fail = ToolBehaviorEvaluator.evaluate_tool_usage(
        tool_calls=tool_calls,
        expected_tool="lookup_customer",
        requires_tool=True,
    )
    assert res_fail.passed is False


@pytest.mark.asyncio
async def test_multi_rubric_llm_judge():
    """Test multi-rubric LLM judge scoring breakdown."""
    judge = CustomLLMJudge(model="test")
    res = await judge.evaluate_multi_rubric(
        user_input="Where is order A100?",
        actual_output="Order A100 is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones.",
        expected_output="Order A100 is Shipped.",
        metadata={"required_keywords": ["A100", "Shipped", "TRK-98765"], "forbidden_keywords": ["FEDEX-9999"]},
    )

    assert isinstance(res, MultiRubricJudgeResult)
    assert res.passed is True
    assert res.overall_score >= 0.90
    assert "accuracy_grounding" in res.rubric_scores
    assert "relevance_completeness" in res.rubric_scores
    assert "policy_compliance" in res.rubric_scores
    assert "tone_security" in res.rubric_scores


@pytest.mark.asyncio
async def test_hybrid_evaluation_engine():
    """Test full hybrid evaluation engine on a test case."""
    engine = HybridEvaluationEngine()
    test_case = Case(
        name="test_order_case",
        inputs="Where is A100?",
        expected_output="Order A100 is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones.",
        metadata={
            "category": "normal",
            "difficulty": "easy",
            "risk": "low",
            "requires_tool": True,
            "expected_tool": "lookup_order",
            "required_keywords": ["A100", "Shipped"],
        },
    )

    result = await engine.evaluate_case(
        case=test_case,
        actual_output="Order A100 is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones.",
        latency_seconds=0.015,
        tool_calls=[{"tool": "lookup_order", "args": {"order_id": "A100"}}],
    )

    assert result.passed is True
    assert result.composite_score >= 0.90
    assert len(result.checks) >= 4
    assert result.judge_breakdown["overall_score"] >= 0.85
