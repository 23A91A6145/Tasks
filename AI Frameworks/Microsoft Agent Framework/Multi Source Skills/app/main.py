import time
import logging
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to sys.path if running directly
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.manager import SkillManager
from agents.assistant import AssistantAgent
from models.skill import Skill

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "logs" / "skills_app.log")
    ]
)
logger = logging.getLogger("SkillsFastAPI")

app = FastAPI(
    title="Multi-Source Skills Provider API",
    description="Backend service for loading, composing, and executing dynamic AI skills.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SkillManager and AssistantAgent
manager = SkillManager()
agent = AssistantAgent(manager)

# Request schemas
class ExecuteRequest(BaseModel):
    name: str = Field(..., description="Name of the skill to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the skill")

class AgentRequest(BaseModel):
    query: str = Field(..., description="Natural language query for the agent")

# API Endpoints
@app.get("/api/skills", tags=["Skills"])
def get_skills():
    """Lists all active skills merged in the registry."""
    registry = manager.get_registry()
    skills = registry.list_skills()
    # Serialize excluding handlers
    return [skill.model_dump() for skill in skills]

@app.get("/api/summary", tags=["Registry"])
def get_summary():
    """Gets conflict statistics, resolution decisions, and load duration."""
    registry = manager.get_registry()
    return registry.summary.model_dump()

@app.post("/api/execute", tags=["Skills"])
def execute_skill(request: ExecuteRequest):
    """Executes a specific skill with the provided JSON arguments."""
    registry = manager.get_registry()
    skill = registry.get_skill(request.name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{request.name}' not found.")
    
    try:
        result = registry.execute(request.name, **request.arguments)
        return {"success": True, "result": result, "skill": skill.model_dump()}
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent", tags=["Agent"])
def query_agent(request: AgentRequest):
    """Sends a natural language query to the Assistant Agent reasoning loop."""
    try:
        response = agent.execute_query(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reload", tags=["Registry"])
def reload_registry():
    """Triggers hot reload of all skill sources and updates the cache."""
    try:
        registry = manager.reload()
        return {
            "success": True, 
            "message": "Registry reloaded successfully", 
            "summary": registry.summary.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload registry: {e}")

class OverrideRequest(BaseModel):
    skill_name: str
    preferred_source: str
    reason: Optional[str] = Field(None, description="Optional explanation for overriding priority")

@app.get("/api/history", tags=["Registry"])
def get_history(limit: int = 50):
    """Returns persistent historical execution logs from SQLite."""
    return manager.db.get_history(limit=limit)

@app.get("/api/metrics", tags=["Registry"])
def get_metrics():
    """Returns aggregated performance metrics for all skills based on execution logs."""
    return manager.db.get_metrics()

@app.post("/api/overrides", tags=["Registry"])
def save_override(request: OverrideRequest):
    """Saves a custom priority override to the database and reloads the registry."""
    try:
        manager.db.save_override(
            skill_name=request.skill_name,
            preferred_source=request.preferred_source,
            reason=request.reason
        )
        manager.reload()
        return {"success": True, "message": f"Override configured for '{request.skill_name}' -> '{request.preferred_source}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/overrides/{skill_name}", tags=["Registry"])
def delete_override(skill_name: str):
    """Deletes a custom priority override from the database and reloads the registry."""
    try:
        manager.db.delete_override(skill_name)
        manager.reload()
        return {"success": True, "message": f"Override removed for '{skill_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the HTML frontend
@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def get_dashboard():
    """Serves the main single-page web dashboard."""
    static_file_path = PROJECT_ROOT / "app" / "static" / "index.html"
    if static_file_path.exists():
        with open(static_file_path, "r") as f:
            return f.read()
    else:
        # Fallback basic page if dashboard HTML isn't created yet
        return """
        <html>
            <head><title>Multi-Source Skills Dashboard</title></head>
            <body>
                <h1>Dashboard loading...</h1>
                <p>Please wait while static files are configured.</p>
            </body>
        </html>
        """

# Ensure static files directory exists and mount it
static_dir = PROJECT_ROOT / "app" / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
