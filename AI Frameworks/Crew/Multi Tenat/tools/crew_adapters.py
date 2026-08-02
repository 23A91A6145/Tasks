"""CrewAI Tool Adapters — Wraps Tool Registry functions into CrewAI BaseTool instances."""

from typing import Any, List
from .registry import registry


def get_crewai_tools() -> List[Any]:
    """Dynamically converts registered tools into CrewAI BaseTools if crewai is installed."""
    tools = []
    try:
        from crewai.tools import BaseTool

        for tool_meta in registry.list_tools():
            name = tool_meta["name"]
            description = tool_meta["description"]

            # Create dynamic BaseTool class for each registered tool
            class DynamicCrewTool(BaseTool):
                name: str = name
                description: str = description

                def _run(self, **kwargs) -> str:
                    res = registry.execute(self.name, **kwargs)
                    if res["success"]:
                        return str(res["result"])
                    return f"Error executing {self.name}: {res.get('error')}"

            tools.append(DynamicCrewTool())
    except ImportError:
        pass
    return tools
