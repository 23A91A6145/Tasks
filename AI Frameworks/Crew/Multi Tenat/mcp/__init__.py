import sys
from pathlib import Path

# Bridge to apps/backend/app/mcp
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.mcp import (
    mcp_client,
    MCPClientManager,
    FilesystemMCPServer,
    GitHubMCPServer,
    BrowserMCPServer,
)

__all__ = [
    "mcp_client",
    "MCPClientManager",
    "FilesystemMCPServer",
    "GitHubMCPServer",
    "BrowserMCPServer",
]
