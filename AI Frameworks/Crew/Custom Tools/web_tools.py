from langchain_core.tools import tool
from pydantic import BaseModel, Field


class WebFetchInput(BaseModel):
    url: str = Field(description="URL to fetch and convert to markdown")
    timeout: int = Field(default=15, ge=1, le=60, description="Request timeout in seconds")


@tool(args_schema=WebFetchInput)
def web_fetch(url: str, timeout: int = 15) -> str:
    """Fetch a URL and extract readable text content as Markdown.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        Markdown-formatted text content from the page.
    """
    try:
        import httpx
    except ImportError:
        return "Error: httpx is required. Install with: pip install crew-tools[web]"

    try:
        resp = httpx.get(url, follow_redirects=True, timeout=timeout)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
    except Exception as e:
        return f"Error fetching URL: {e}"

    if "image" in content_type:
        return f"Error: URL returned image content ({content_type})"

    text = resp.text

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        body = soup.find("body") or soup
        lines = []
        for el in body.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "pre", "blockquote", "td", "th", "caption"]):
            tag = el.name
            text_content = el.get_text(strip=True)
            if not text_content:
                continue
            if tag.startswith("h"):
                level = tag[1]
                lines.append(f"{'#' * int(level)} {text_content}")
            elif tag == "li":
                lines.append(f"- {text_content}")
            elif tag == "pre":
                lines.append(f"```\n{text_content}\n```")
            elif tag in ("td", "th"):
                lines.append(f"| {text_content} |")
            elif tag == "caption":
                lines.append(f"*{text_content}*")
            else:
                lines.append(text_content)
        result = "\n\n".join(lines)
        if not result.strip():
            result = body.get_text(strip=True)
        return result[:10000] if len(result) > 10000 else result
    except ImportError:
        return text[:5000]
    except Exception as e:
        return f"Error parsing HTML: {e}"


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, ge=1, le=20, description="Number of results to return")


@tool(args_schema=WebSearchInput)
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo.

    Args:
        query: The search query.
        max_results: Number of results to return.

    Returns:
        Formatted search results with title, snippet, and URL.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return "Error: duckduckgo_search is required. Install with: pip install crew-tools[web]"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"Error performing search: {e}"

    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        snippet = r.get("body", "")
        url = r.get("href", "")
        lines.append(f"{i}. **{title}**")
        if snippet:
            lines.append(f"   {snippet[:200]}")
        if url:
            lines.append(f"   {url}")
        lines.append("")
    return "\n".join(lines)


class RSSParseInput(BaseModel):
    url: str = Field(description="URL of the RSS/Atom feed")
    max_entries: int = Field(default=10, ge=1, le=50, description="Maximum entries to return")


@tool(args_schema=RSSParseInput)
def rss_parse(url: str, max_entries: int = 10) -> str:
    """Parse an RSS or Atom feed and return recent entries.

    Args:
        url: Feed URL.
        max_entries: Maximum number of entries.

    Returns:
        Formatted feed entries with title, date, link, and summary.
    """
    try:
        import xml.etree.ElementTree as ET

        import httpx
    except ImportError:
        return "Error: httpx is required. Install with: pip install crew-tools[web]"

    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
    except Exception as e:
        return f"Error fetching/parsing feed: {e}"


    entries = []

    for item in root.iter("item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        pubdate = item.findtext("pubDate", "")
        desc = item.findtext("description", "")[:300]
        entries.append((title, pubdate, link, desc))

    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        pubdate = entry.findtext("{http://www.w3.org/2005/Atom}updated", "")
        desc_el = entry.find("{http://www.w3.org/2005/Atom}content")
        desc = (desc_el.text or "")[:300] if desc_el is not None else ""
        entries.append((title, pubdate, link, desc))

    if not entries:
        return "No entries found in feed."

    entries = entries[:max_entries]
    lines = []
    for i, (title, pubdate, link, desc) in enumerate(entries, 1):
        lines.append(f"{i}. {title or 'Untitled'}")
        if pubdate:
            lines.append(f"   Date: {pubdate}")
        if link:
            lines.append(f"   Link: {link}")
        if desc:
            lines.append(f"   {desc}")
        lines.append("")
    return "\n".join(lines)
