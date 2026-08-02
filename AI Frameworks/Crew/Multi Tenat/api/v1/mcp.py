from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from ...api.deps import get_workspace_membership, require_role
from ...core.permissions import ROLE_ADMIN
from ...mcp.client import mcp_client
from ...models import Membership

router = APIRouter(prefix="/workspaces/{slug}/mcp", tags=["mcp"])


class MCPCallRequest(BaseModel):
    server_id: str = Field(..., description="Target MCP server ID (filesystem | github | browser)")
    tool_name: str = Field(..., description="MCP tool name to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool execution arguments")


@router.get("/servers", response_model=List[Dict[str, Any]])
def list_mcp_servers(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
) -> List[Dict[str, Any]]:
    """List all registered Model Context Protocol (MCP) servers and their resources & tools."""
    return mcp_client.list_servers()


@router.post("/call", response_model=Dict[str, Any])
def call_mcp_tool(
    slug: str,
    body: MCPCallRequest,
    membership: Membership = Depends(require_role(ROLE_ADMIN)),
) -> Dict[str, Any]:
    """Invoke an MCP tool on a target MCP server."""
    res = mcp_client.call_tool(body.server_id, body.tool_name, body.arguments)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "MCP Tool call failed"))
    return res
