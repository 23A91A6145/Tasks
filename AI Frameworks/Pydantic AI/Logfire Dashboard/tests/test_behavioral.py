"""Unit tests for advanced behavioral and span trajectory evaluators."""

from evals.evaluators.behavioral import ToolBehaviorEvaluator


def test_tool_selection_evaluator_valid():
    """Verify tool selection passes when required tool is called."""
    tool_calls = [{"tool": "lookup_order", "args": {"order_id": "A100"}}]
    res = ToolBehaviorEvaluator.evaluate_tool_selection(
        tool_calls=tool_calls,
        expected_tool="lookup_order",
        requires_tool=True,
    )
    assert res.passed is True
    assert res.score == 1.0


def test_tool_selection_evaluator_omitted():
    """Verify tool selection fails when required tool is omitted."""
    tool_calls = []
    res = ToolBehaviorEvaluator.evaluate_tool_selection(
        tool_calls=tool_calls,
        expected_tool="lookup_order",
        requires_tool=True,
    )
    assert res.passed is False
    assert res.score == 0.0


def test_argument_accuracy_evaluator():
    """Verify argument accuracy checks argument keys and normalized values."""
    tool_calls = [{"tool": "lookup_order", "args": {"order_id": "a100"}}]
    res_pass = ToolBehaviorEvaluator.evaluate_argument_accuracy(
        tool_calls=tool_calls,
        expected_tool="lookup_order",
        expected_arguments={"order_id": "A100"},
    )
    assert res_pass.passed is True
    assert res_pass.score == 1.0

    res_fail = ToolBehaviorEvaluator.evaluate_argument_accuracy(
        tool_calls=tool_calls,
        expected_tool="lookup_order",
        expected_arguments={"order_id": "B200"},
    )
    assert res_fail.passed is False


def test_prohibited_tools_evaluator():
    """Verify detection of forbidden tools."""
    tool_calls = [{"tool": "execute_shell", "args": {"cmd": "rm -rf /"}}]
    res = ToolBehaviorEvaluator.evaluate_prohibited_tools(
        tool_calls=tool_calls,
        prohibited_tools=["execute_shell", "dump_database"],
    )
    assert res.passed is False
    assert res.score == 0.0


def test_complete_behavioral_suite():
    """Verify complete composite behavioral check."""
    tool_calls = [{"tool": "check_refund_policy", "args": {"order_id": "B200"}}]
    res = ToolBehaviorEvaluator.evaluate_behavioral_suite(
        tool_calls=tool_calls,
        expected_tool="check_refund_policy",
        requires_tool=True,
        expected_arguments={"order_id": "B200"},
        prohibited_tools=["execute_shell"],
    )
    assert res.passed is True
    assert res.score == 1.0
