import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.database import init_db
from backend.app.api.health import router as health_router
from backend.app.api.routes import router as research_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ResearchOS database...")
    await init_db()
    logger.info(f"ResearchOS backend v{settings.APP_VERSION} started successfully.")
    yield
    logger.info("ResearchOS backend shutting down.")

app = FastAPI(
    title="ResearchOS API",
    version=settings.APP_VERSION,
    description="Production Agentic AI Research Intelligence Platform API",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API routes first
app.include_router(health_router)
app.include_router(research_router)

# Mount Frontend static production build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist):
    logger.info(f"Mounting static frontend from {frontend_dist}")
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
