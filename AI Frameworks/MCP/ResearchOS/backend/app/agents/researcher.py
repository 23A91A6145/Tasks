import asyncio
from typing import List
from backend.app.models.schemas import SourceDocument, ResearchPlan
from backend.app.sources.arxiv import search_arxiv
from backend.app.sources.openalex import search_openalex
from backend.app.sources.semantic_scholar import search_semantic_scholar
from backend.app.sources.tavily import search_web_tavily
from backend.app.retrieval.reranker import EvidenceReranker
from backend.app.core.logging import logger

class ResearcherAgent:
    """Executes multi-source concurrent retrieval across academic and web repositories."""

    @staticmethod
    async def collect_sources(plan: ResearchPlan, max_sources: int = 20) -> List[SourceDocument]:
        tasks = []
        # Dispatch queries concurrently
        for sq in plan.sub_questions[:3]:
            for query in sq.search_queries[:2]:
                tasks.append(search_arxiv(query, max_results=3))
                tasks.append(search_openalex(query, max_results=3))
                tasks.append(search_web_tavily(query, max_results=3))
                tasks.append(search_semantic_scholar(query, max_results=2))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_sources: List[SourceDocument] = []

        for r in results:
            if isinstance(r, list):
                all_sources.extend(r)
            elif isinstance(r, Exception):
                logger.warning(f"Retrieval task exception: {r}")

        # Rerank and deduplicate
        filtered = EvidenceReranker.rerank_sources(all_sources, top_n=max_sources)
        return filtered
