import pytest
from backend.app.research.citations import CitationVerifier

@pytest.mark.asyncio
async def test_citation_passage_grounding():
    verifier = CitationVerifier()
    source_snippet = "LangGraph introduces cyclical graph execution where node state is persisted across transitions."
    passage_exact = "cyclical graph execution where node state is persisted"
    passage_absent = "quantum neural networks running on superconducting qubits"

    score_match = verifier.check_passage_grounding(passage_exact, source_snippet)
    score_nomatch = verifier.check_passage_grounding(passage_absent, source_snippet)

    assert score_match > 0.8
    assert score_nomatch < 0.3

@pytest.mark.asyncio
async def test_link_health_validation():
    verifier = CitationVerifier()
    assert await verifier.verify_link_health("https://arxiv.org/abs/2601.01123") is True
    assert await verifier.verify_link_health("invalid-url-string") is False
