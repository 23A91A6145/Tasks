from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

app = FastAPI(
    title="AI Customer Support Multi-Agent System API",
    description="FastAPI service wrapper around Microsoft Agent Framework Handoff Workflow",
    version="1.0.0"
)

# Enable CORS (critical for React/Vite dashboard integrations)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

app.include_router(api_router, prefix="/api")

# Ensure static directory exists
os.makedirs("app/static", exist_ok=True)

# Mount the static files to serve the dashboard frontend
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

