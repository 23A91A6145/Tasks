# app/api.py

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent import classify_ticket_content
from app.database import init_db, save_classification, get_tickets, get_metrics, reclassify_ticket_db
from app.config import LLM_MODEL, ENV

# Initialize database
init_db()

app = FastAPI(
    title="Structured Ticket Classifier API",
    description="Type-safe AI support ticket categorization, prioritization, and routing",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define schemas for API
class TicketRequest(BaseModel):
    message: str = Field(
        ..., 
        description="The raw unstructured text message from the customer",
        examples=["I was charged twice for my subscription this month."]
    )

class ClassificationResponse(BaseModel):
    id: int = Field(description="The unique database ID of the ticket")
    ticket_message: str
    category: str
    secondary_category: Optional[str] = None
    priority: str
    suggested_agent: str
    confidence: float
    summary: str
    reasoning: str
    requires_human_review: bool
    model_used: str
    processing_time_ms: int
    original_category: Optional[str] = None
    original_priority: Optional[str] = None
    is_reclassified: bool = False

# Health endpoint
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "model": LLM_MODEL,
        "environment": ENV
    }

# Classification endpoint
@app.post("/api/v1/tickets/classify", response_model=ClassificationResponse)
def classify_ticket(payload: TicketRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Ticket message cannot be empty")
        
    try:
        # Run classification agent
        result, duration_ms = classify_ticket_content(payload.message)
        
        # Save to database
        ticket_id = save_classification(payload.message, result, LLM_MODEL, duration_ms)
        
        return ClassificationResponse(
            id=ticket_id,
            ticket_message=payload.message,
            category=result.category.value,
            secondary_category=result.secondary_category.value if result.secondary_category else None,
            priority=result.priority.value,
            suggested_agent=result.suggested_agent.value,
            confidence=result.confidence,
            summary=result.summary,
            reasoning=result.reasoning,
            requires_human_review=result.requires_human_review,
            model_used=LLM_MODEL,
            processing_time_ms=duration_ms,
            original_category=result.category.value,
            original_priority=result.priority.value,
            is_reclassified=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

# Get past tickets
@app.get("/api/v1/tickets")
def get_classified_tickets(limit: int = 50, offset: int = 0):
    try:
        return get_tickets(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tickets: {str(e)}")

# Get metrics
@app.get("/api/v1/metrics")
def get_analytics_metrics():
    try:
        return get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")

class ReclassifyRequest(BaseModel):
    category: str
    priority: str
    suggested_agent: str

@app.post("/api/v1/tickets/{ticket_id}/reclassify")
def reclassify_ticket(ticket_id: int, payload: ReclassifyRequest):
    try:
        from app.models import TicketCategory, TicketPriority, SuggestedAgent
        # Validate values exist as valid enum values
        TicketCategory(payload.category)
        TicketPriority(payload.priority)
        SuggestedAgent(payload.suggested_agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid classification values: {str(e)}")
        
    success = reclassify_ticket_db(
        ticket_id=ticket_id,
        new_category=payload.category,
        new_priority=payload.priority,
        new_agent=payload.suggested_agent
    )
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    return {"status": "success", "message": "Ticket reclassified successfully"}

# UI serving
@app.get("/", response_class=HTMLResponse)
async def read_index():
    static_index = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_index):
        with open(static_index, "r") as f:
            return f.read()
    else:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Structured Ticket Classifier</title></head>
                <body style="font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background-color: #0f172a; color: #f8fafc;">
                    <h1>Structured Ticket Classifier UI</h1>
                    <p>Static index.html not found. Place your frontend file in app/static/index.html.</p>
                    <p>The API endpoints are live:</p>
                    <ul>
                        <li><a href="/docs" style="color: #3b82f6;">Swagger API Docs</a></li>
                        <li><a href="/api/v1/health" style="color: #3b82f6;">Health Check Endpoint</a></li>
                    </ul>
                </body>
            </html>
            """,
            status_code=404
        )

# Mount static files directory if it exists
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")
