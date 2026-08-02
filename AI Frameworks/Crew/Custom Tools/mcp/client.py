"""MCP Client Manager — Dispatches calls to registered MCP Servers (Filesystem, GitHub, Browser)."""

from typing import Any, Dict, List, Optional
from .browser_mcp import BrowserMCPServer
from .filesystem_mcp import FilesystemMCPServer, make_filesystem_server
from .github_mcp import GitHubMCPServer


class MCPClientManager:
    """Orchestrates MCP servers and dispatches tool execution requests."""

    def __init__(self, root_dir: Optional[str] = None):
        self.servers = {
            "filesystem": FilesystemMCPServer(root_dir=root_dir) if root_dir else make_filesystem_server(),
            "github": GitHubMCPServer(),
            "browser": BrowserMCPServer(),
        }

    def list_servers(self) -> List[Dict[str, Any]]:
        """List active MCP servers and their capabilities."""
        results = []
        for server_id, server in self.servers.items():
            results.append({
                "id": server_id,
                "name": server_id.capitalize() + " MCP Server",
                "resources": server.list_resources(),
                "tools": server.list_tools(),
            })
        return results

    def call_tool(self, server_id: str, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatch JSON-RPC / MCP tool call to the specified server."""
        server = self.servers.get(server_id)
        if not server:
            return {"success": False, "error": f"MCP Server '{server_id}' not found"}
        args = arguments or {}
        try:
            res = server.execute_tool(tool_name, args)
            if "error" in res:
                return {"success": False, "server": server_id, "tool": tool_name, "error": res["error"]}
            return {"success": True, "server": server_id, "tool": tool_name, "result": res}
        except Exception as e:
            return {"success": False, "server": server_id, "tool": tool_name, "error": str(e)}


mcp_client = MCPClientManager()
