from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .api.router import api_router
from .core.config import settings
from .core.database import engine, init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="5.0.0",
    description=(
        "Multi-tenant AI support platform: tenant-scoped auth & RBAC, per-tenant "
        "knowledge (RAG), a checkpointed AI ticket/support crew with human approval, "
        "flows, tools, MCP servers, plans & usage metering, jobs, analytics, a public "
        "widget and outbound webhooks."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.APP_NAME,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health")
def health() -> dict:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
