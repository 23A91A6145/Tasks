import os
import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError

from app.config import (
    HOST,
    PORT,
    AUDIT_LOG_PATH,
    APPROVAL_LOG_PATH,
    ERROR_LOG_PATH,
    LLM_PROVIDER,
    MAX_AUTO_APPROVE_AMOUNT,
    MANAGER_LIMIT,
    APPROVAL_SLA_TIMEOUT_SECONDS,
    RATE_LIMIT_PER_MINUTE,
    SEED_DEMO_DATA,
)
from app.models import DecisionInput
from app.utils import logger, log_error
from app.agent import ChatAgent
from app.approval import (
    handle_approval_decision,
    get_all_approval_requests,
    get_approval_request,
    save_approval_request,
)
from app.services import (
    get_dashboard_stats,
    save_notification,
    get_notification_outbox,
)
from app.refund_tool import FRAMEWORK_AVAILABLE
from app.middleware import RateLimitMiddleware

app = FastAPI(
    title="Approval-Gated Refund Agent HITL",
    description="Safety-critical Human-in-the-Loop refund manager built on Microsoft Agent Framework concepts.",
    version="2.0.0",
)

# Apply Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, limit=RATE_LIMIT_PER_MINUTE, window=60)


# Centralized exception handlers (Phase 4.4 - Error Handling)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    detail = "; ".join(f"{'.'.join(str(p) for p in e.get('loc', []))}: {e.get('msg')}" for e in errors)
    log_error(f"Validation failure on {request.url.path}: {detail}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "message": detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log_error(f"Unhandled error on {request.url.path}: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": str(exc)},
    )


# Initialize Chat Agent
agent = ChatAgent(
    name="RefundSafetyAgent",
    instructions=(
        "You are a compliance-first refund processing agent. You parse refund requests, "
        "validate them against corporate safety rules, and route them to human gates if "
        "they require approval. You never execute payments without a human authorization."
    ),
)


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def api_health():
    """Liveness & capability probe used by Docker healthchecks."""
    return {
        "status": "healthy",
        "service": "Approval-Gated Refund Agent",
        "version": app.version,
        "framework": "Microsoft Agent Framework (compatible)" if FRAMEWORK_AVAILABLE else "Simulated MAF runtime",
        "llm_provider": LLM_PROVIDER,
        "time": datetime.now().isoformat(),
    }


@app.get("/api/info")
async def api_info():
    """Exposes the active policy configuration for the compliance dashboard."""
    return {
        "llm_provider": LLM_PROVIDER,
        "max_auto_approve_amount": MAX_AUTO_APPROVE_AMOUNT,
        "manager_limit": MANAGER_LIMIT,
        "approval_sla_timeout_seconds": APPROVAL_SLA_TIMEOUT_SECONDS,
        "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE,
        "seed_demo_data": SEED_DEMO_DATA,
        "framework_available": FRAMEWORK_AVAILABLE,
    }


# ---------------------------------------------------------------------------
# Data endpoints
# ---------------------------------------------------------------------------
@app.get("/api/stats")
async def api_stats():
    """Retrieve current dashboard stats."""
    try:
        stats = get_dashboard_stats()
        return stats.model_dump()
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/approvals")
async def api_approvals():
    """Retrieve all approval requests (sorted by created_at)."""
    try:
        reqs = get_all_approval_requests()
        sorted_reqs = sorted(
            reqs.values(),
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )
        return sorted_reqs
    except Exception as e:
        logger.error(f"Error fetching approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/approvals/{request_id}")
async def api_approval_detail(request_id: str):
    """Retrieve detail of a specific approval request."""
    req = get_approval_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req.model_dump()


@app.get("/api/notifications")
async def api_notifications():
    """Retrieve the persisted notification outbox (customer emails + internal alerts)."""
    return get_notification_outbox()


# ---------------------------------------------------------------------------
# Chat agent endpoint
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    message: str


@app.post("/api/chat")
async def api_chat(payload: ChatMessage):
    """Submit a message to the AI agent to trigger a refund flow."""
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    try:
        response = agent.run(payload.message)
        if response.get("status") == "approval_required":
            approval_req = response["approval_req"]
            save_approval_request(approval_req)
            response["approval_req"] = approval_req.model_dump()
        elif response.get("status") == "auto_approved":
            approval_req = response["approval_req"]
            response["approval_req"] = approval_req.model_dump()
            response["notifications"] = save_notification(approval_req)
        return response
    except Exception as e:
        logger.error(f"Chat agent execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Reviewer decision endpoint
# ---------------------------------------------------------------------------
@app.post("/api/approvals/{request_id}/decision")
async def api_decision(request_id: str, decision: DecisionInput, request: Request):
    """Submit a reviewer decision (Approve/Reject/Hold/Escalate) on a pending request."""
    ip_address = request.client.host if request.client else "127.0.0.1"
    session_id = request.headers.get("x-session-id", "SESSION-SIM-DEFAULT")

    try:
        result = handle_approval_decision(
            request_id=request_id,
            decision=decision,
            ip_address=ip_address,
            session_id=session_id,
        )

        # Persist + attach notification templates for finalized decisions
        req = get_approval_request(request_id)
        if req:
            result["notifications"] = save_notification(req)

        return result
    except PermissionError as pe:
        logger.warning(f"Authorization failure: {pe}")
        return JSONResponse(status_code=403, content={"error": "Forbidden", "message": str(pe)})
    except ValueError as ve:
        logger.warning(f"Bad Request: {ve}")
        return JSONResponse(status_code=400, content={"error": "Bad Request", "message": str(ve)})
    except FileNotFoundError as fe:
        logger.warning(f"Missing checkpoint: {fe}")
        return JSONResponse(status_code=409, content={"error": "Workflow State Missing", "message": str(fe)})
    except Exception as e:
        logger.error(f"Unexpected error handling decision for {request_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Demo / operational endpoints
# ---------------------------------------------------------------------------
@app.post("/api/seed/reset")
async def api_seed_reset():
    """Re-seed demo data (for presentations / hands-on sessions)."""
    from app.approval import _seed_database, DB_FILE
    from app.settings import settings as app_settings
    import glob

    for f_path in glob.glob(str(app_settings.checkpoint_dir / "*.json")):
        if str(DB_FILE) in f_path:
            continue
        try:
            os.unlink(f_path)
        except OSError:
            pass
    if DB_FILE.exists():
        DB_FILE.unlink()
    data = _seed_database()
    return {"status": "success", "seeded": len(data)}


# ---------------------------------------------------------------------------
# Logs endpoint
# ---------------------------------------------------------------------------
@app.get("/api/logs/{log_type}")
async def api_logs(log_type: str):
    """Read contents of logs for dashboard rendering."""
    log_map = {
        "audit": AUDIT_LOG_PATH,
        "approvals": APPROVAL_LOG_PATH,
        "errors": ERROR_LOG_PATH,
    }

    if log_type not in log_map:
        raise HTTPException(status_code=400, detail="Invalid log type")

    path = log_map[log_type]
    if not path.exists():
        return []

    try:
        with open(path, "r") as f:
            lines = f.readlines()

        if log_type == "audit":
            parsed_lines = []
            for line in lines[-50:]:
                try:
                    parsed_lines.append(json.loads(line.strip()))
                except Exception:
                    parsed_lines.append({"raw": line.strip()})
            return parsed_lines
        return [line.strip() for line in lines[-50:]]
    except Exception as e:
        logger.error(f"Error reading log file {log_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read logs")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
