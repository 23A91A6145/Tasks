import time
from typing import Any

from crew_tools import TOOL_REGISTRY
from crew_tools._config import load_config
from crew_tools._logging import get_logger, request_id

log = get_logger("api")

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError:
    FastAPI = None
    BaseModel = object

    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail


class InvokeRequest(BaseModel):
    args: dict[str, Any] = Field(default_factory=dict)


class InvokeResponse(BaseModel):
    tool: str
    result: Any = None
    error: str | None = None
    execution_ms: float = 0.0


def _build_app() -> Any:
    if FastAPI is None:
        raise RuntimeError("fastapi not installed. Run: pip install crew-tools[api]")

    app = FastAPI(
        title="Crew Tools API",
        version="0.1.0",
        description="REST API for all 27+ LangChain-compatible tools",
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "tools": len(TOOL_REGISTRY)}

    @app.get("/tools")
    async def list_tools():
        return {
            "tools": [
                {
                    "name": name,
                    "description": (
                        getattr(t, "description", None) or
                        (t.__doc__ or "").strip().split("\n")[0]
                    ),
                }
                for name, t in sorted(TOOL_REGISTRY.items())
            ],
            "count": len(TOOL_REGISTRY),
        }

    @app.post("/tools/{name}/invoke", response_model=InvokeResponse)
    async def invoke_tool(name: str, req: InvokeRequest):
        import uuid
        rid = str(uuid.uuid4())[:8]
        token = request_id.set(rid)
        try:
            tool = TOOL_REGISTRY.get(name)
            if tool is None:
                raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")
            start = time.monotonic()
            kwargs = req.args
            try:
                if hasattr(tool, "ainvoke"):
                    result = await tool.ainvoke(kwargs)
                else:
                    result = tool.invoke(kwargs)
            except Exception as e:
                elapsed = (time.monotonic() - start) * 1000
                log.warning("Tool '%s' failed: %s", name, e)
                return InvokeResponse(tool=name, error=str(e), execution_ms=round(elapsed, 1))
            elapsed = (time.monotonic() - start) * 1000
            log.info("Tool '%s' OK in %.1fms", name, elapsed)
            return InvokeResponse(tool=name, result=result, execution_ms=round(elapsed, 1))
        finally:
            request_id.reset(token)

    return app


app = _build_app() if FastAPI is not None else None


def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    import uvicorn
    cfg = load_config()
    uvicorn.run(
        "crew_tools.api_server:app",
        host=host or cfg.server.host,
        port=port or cfg.server.port,
        reload=reload or cfg.server.reload,
        log_level="info",
    )
