from typing import List
from backend.app.models.schemas import SourceDocument
from backend.app.sources.tavily import search_web_tavily

async def search_brave(query: str, max_results: int = 5) -> List[SourceDocument]:
    """Brave search interface routing through unified web search."""
    return await search_web_tavily(query, max_results)
