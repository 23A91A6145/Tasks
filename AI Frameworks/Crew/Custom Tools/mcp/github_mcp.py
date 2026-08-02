"""GitHub MCP Server — Integration for GitHub code search, issues, and PR reference inspection."""

from typing import Any, Dict, List


class GitHubMCPServer:
    """Model Context Protocol server for GitHub repository and issue management."""

    def list_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "uri": "github://repo/issues",
                "name": "GitHub Tenant Support Issues",
                "mimeType": "application/json",
                "description": "Active GitHub support tickets and developer issues",
            }
        ]

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "github_search_code",
                "description": "Search code repository for matching symbols or errors.",
                "parameters": {"query": {"type": "string"}, "repo": {"type": "string"}},
            },
            {
                "name": "github_create_issue",
                "description": "Create a new issue on GitHub repository.",
                "parameters": {
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
            },
            {
                "name": "github_get_file_content",
                "description": "Fetch repository file content by path.",
                "parameters": {"repo": {"type": "string"}, "path": {"type": "string"}},
            },
        ]

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        if name == "github_search_code":
            query = kwargs.get("query", "")
            repo = kwargs.get("repo", "tenantdesk/saas-core")
            return {
                "repo": repo,
                "query": query,
                "matches": [
                    {
                        "path": "src/api/auth.ts",
                        "line": 42,
                        "snippet": f"// Handled query: {query}",
                    },
                    {
                        "path": "docs/troubleshooting.md",
                        "line": 15,
                        "snippet": f"# Troubleshooting {query}",
                    },
                ],
            }
        elif name == "github_create_issue":
            repo = kwargs.get("repo", "org/support-repo")
            title = kwargs.get("title", "Support Issue")
            body = kwargs.get("body", "")
            issue_num = abs(hash(title)) % 900 + 100
            return {
                "status": "created",
                "repo": repo,
                "issue_number": issue_num,
                "url": f"https://github.com/{repo}/issues/{issue_num}",
                "title": title,
            }
        elif name == "github_get_file_content":
            path = kwargs.get("path", "README.md")
            return {
                "path": path,
                "content": f"# {path}\n\nAutomated documentation for GitHub MCP integration.",
            }
        return {"error": f"Unknown GitHub MCP tool '{name}'"}
