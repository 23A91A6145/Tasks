from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from ...api.deps import get_workspace_membership, require_role
from ...core.permissions import ROLE_ADMIN
from ...models import Membership
from ...tools.registry import registry

router = APIRouter(prefix="/workspaces/{slug}/tools", tags=["tools"])


class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to tool")


@router.get("", response_model=List[Dict[str, Any]])
def list_tools(
    slug: str,
    category: Optional[str] = None,
    membership: Membership = Depends(get_workspace_membership),
) -> List[Dict[str, Any]]:
    """List all available tools in the tenant tool ecosystem."""
    return registry.list_tools(category=category)


@router.post("/execute", response_model=Dict[str, Any])
def execute_tool(
    slug: str,
    body: ToolExecuteRequest,
    membership: Membership = Depends(require_role(ROLE_ADMIN)),
) -> Dict[str, Any]:
    """Execute a built-in platform tool (calculator, CRM, web search, email, calendar, github)."""
    res = registry.execute(body.tool_name, **body.arguments)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Execution failed"))
    return res
