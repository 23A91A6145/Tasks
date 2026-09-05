import pytest
from backend.app.models.schemas import ResearchCreateRequest
from backend.app.core.constants import ResearchMode, RunStatus
from backend.app.research.execution import ResearchExecutionEngine

@pytest.mark.asyncio
async def test_end_to_end_research_pipeline():
    req = ResearchCreateRequest(
        query="Compare LangGraph and CrewAI for production enterprise systems in 2026",
        mode=ResearchMode.DEEP,
        max_sources=5
    )
    res = await ResearchExecutionEngine.execute_research(req)
    
    assert res.status == RunStatus.COMPLETED
    assert res.sources_count > 0
    assert res.claims_count > 0
    assert res.citations_count > 0
    assert res.report is not None
    assert len(res.report.sections) >= 3
    assert res.trace is not None
    assert len(res.trace.steps) >= 5
    assert res.critic_score is not None and res.critic_score >= 80
