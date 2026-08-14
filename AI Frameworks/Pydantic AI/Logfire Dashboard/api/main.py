"""AgentEval Lab - Production FastAPI Evaluation & Observability Service."""

from __future__ import annotations

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in sys.path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.routes.datasets import router as datasets_router
from api.routes.experiments import router as experiments_router
from api.routes.regressions import router as regressions_router
from evals.observability import tracer

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize OpenTelemetry and Logfire tracing on service startup."""
    tracer.init_logfire()
    yield

app = FastAPI(
    title="AgentEval Lab API",
    description="Production-Grade AI Evaluation, Observability & Regression Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for local or distributed access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(datasets_router)
app.include_router(experiments_router)
app.include_router(regressions_router)

FRONTEND_INDEX = PROJECT_ROOT / "frontend" / "index.html"




@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AgentEval Lab API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


@app.get("/", response_class=HTMLResponse, tags=["ui"])
def serve_dashboard() -> FileResponse:
    """Serve the interactive web UI dashboard."""
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return HTMLResponse("<h2>AgentEval Lab Dashboard index.html not found</h2>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
