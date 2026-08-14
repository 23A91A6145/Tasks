"""Unit tests for Logfire observability and span tracing."""

from evals.observability import EvaluationTracer, SpanRecord


def test_tracer_initialization():
    """Verify tracer initializes safely with local fallback."""
    tracer = EvaluationTracer()
    assert tracer is not None


def test_span_lifecycle():
    """Verify hierarchical span creation, timing, and attribute recording."""
    tracer = EvaluationTracer()
    
    with tracer.start_span("test.parent_case", attributes={"case_id": "case_01"}) as parent:
        assert parent.name == "test.parent_case"
        assert parent.attributes["case_id"] == "case_01"

        with tracer.start_span("test.tool_call", attributes={"tool": "lookup_order"}) as child:
            assert child.name == "test.tool_call"
            assert child.attributes["tool"] == "lookup_order"

    assert parent.duration_ms >= 0
    assert len(parent.children) == 1
    assert parent.children[0].name == "test.tool_call"


def test_export_trace_tree():
    """Verify structured trace tree export."""
    tracer = EvaluationTracer()
    
    with tracer.start_span("eval.root", attributes={"model": "test"}) as root:
        with tracer.start_span("eval.deterministic"):
            pass

    tree = tracer.export_trace_tree(root)
    assert tree["name"] == "eval.root"
    assert tree["attributes"]["model"] == "test"
    assert len(tree["children"]) == 1
    assert tree["children"][0]["name"] == "eval.deterministic"
