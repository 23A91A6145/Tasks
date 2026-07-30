from crewai.tools import tool
from duckduckgo_search import DDGS


@tool("Web Search")
def web_search_tool(query: str) -> str:
    """Searches the web for current, up-to-date information.
    Use this for any question that requires live data from the internet:
    recent news, documentation, error solutions, product comparisons,
    pricing details, or any topic where your training knowledge may be outdated."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No search results found."
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            lines.append(f"{i}. {title}\n   {body}\n   Source: {href}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Web search failed: {e}"
