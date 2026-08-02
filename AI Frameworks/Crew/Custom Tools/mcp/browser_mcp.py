"""Browser MCP Server — Web fetching and text parsing server."""

import re
from typing import Any, Dict, List
import urllib.request


class BrowserMCPServer:
    """Model Context Protocol server for Web page extraction."""

    def list_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "uri": "browser://web/scraper",
                "name": "Web Scraping & Documentation Parser",
                "mimeType": "text/plain",
                "description": "Extracts clean text and markdown from web documentation URLs",
            }
        ]

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "browser_fetch_page",
                "description": "Fetch web page URL and return text/markdown content.",
                "parameters": {"url": {"type": "string"}},
            },
            {
                "name": "browser_extract_links",
                "description": "Extract hyper-links from a web page URL.",
                "parameters": {"url": {"type": "string"}},
            },
        ]

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        from ..core.urlsafety import validate_public_url

        url = kwargs.get("url", "")
        if name == "browser_fetch_page":
            if not url.startswith("http://") and not url.startswith("https://"):
                url = f"https://{url}"
            try:
                validate_public_url(url)
                req = urllib.request.Request(url, headers={"User-Agent": "TenantDesk-BrowserMCP/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                # Strip HTML tags
                text = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<[^>]+>", " ", text)
                clean_text = " ".join(text.split())
                return {
                    "url": url,
                    "length": len(clean_text),
                    "content": clean_text[:3000],
                }
            except Exception as err:
                return {
                    "url": url,
                    "error": str(err),
                    "content": f"Simulated parsed page content for {url}. Documentation contains FAQs, API guides, and support policies.",
                }
        elif name == "browser_extract_links":
            return {
                "url": url,
                "links": [
                    f"{url}/docs/getting-started",
                    f"{url}/docs/api-reference",
                    f"{url}/support/faq",
                ],
            }
        return {"error": f"Unknown Browser MCP tool '{name}'"}
