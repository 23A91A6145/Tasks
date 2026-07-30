import csv
import io
import json
import logging
import sys
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from crews.support_crew import SupportCrew
from api.history_store import HistoryStore

logger = logging.getLogger(__name__)

store = HistoryStore()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    store.close()


app = FastAPI(
    title="Support Triage API",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str = ""


class ChatResponse(BaseModel):
    id: int
    conversation_id: str
    query: str
    classification: str
    tools_used: list[str]
    routing_rationale: str
    response: str
    validated: bool
    validation_report: str
    execution_time: float


class FeedbackRequest(BaseModel):
    feedback: int = Field(..., ge=-1, le=1)


class HistoryEntry(BaseModel):
    id: int
    conversation_id: str
    timestamp: str
    query: str
    classification: str
    tools_used: list[str]
    routing_rationale: str
    response: str
    validated: bool
    validation_report: str
    execution_time: float
    feedback: Optional[int] = None


class HistoryResponse(BaseModel):
    entries: list[HistoryEntry]
    total: int
    limit: int
    offset: int


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.1.0"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    request_id = uuid.uuid4().hex[:8]
    conv_id = req.conversation_id or f"conv_{uuid.uuid4().hex[:12]}"

    conversation_history = []
    if req.conversation_id:
        entries = store.get_conversation(req.conversation_id, limit=10)
        conversation_history = [
            {"role": "user", "content": e["query"]}
            for e in reversed(entries)
        ]

    try:
        start = time.time()
        crew = SupportCrew(req.query, conversation_history=conversation_history)
        result = crew.run()
        elapsed = round(time.time() - start, 2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Chat request %s failed: %s", request_id, e)
        raise HTTPException(status_code=500, detail="Internal processing error")

    entry_id = store.add_entry(
        query=result["query"],
        classification=result["classification"],
        tools_used=result.get("tools_used", []),
        routing_rationale=result.get("routing_rationale", ""),
        response=result["response"],
        validated=result.get("validated", False),
        validation_report=result.get("validation_report", ""),
        execution_time=elapsed,
        conversation_id=conv_id,
    )

    return ChatResponse(
        id=entry_id,
        conversation_id=conv_id,
        query=result["query"],
        classification=result["classification"],
        tools_used=result.get("tools_used", []),
        routing_rationale=result.get("routing_rationale", ""),
        response=result["response"],
        validated=result.get("validated", False),
        validation_report=result.get("validation_report", ""),
        execution_time=elapsed,
    )


@app.get("/history", response_model=HistoryResponse)
def get_history(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    classification: str = "",
    search: str = "",
    conversation_id: str = "",
):
    entries = store.get_all(
        limit=limit, offset=offset,
        classification=classification,
        search=search,
        conversation_id=conversation_id,
    )
    total = store.count(
        classification=classification,
        search=search,
        conversation_id=conversation_id,
    )
    return HistoryResponse(
        entries=[HistoryEntry(**e) for e in entries],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.get("/history/{entry_id}", response_model=HistoryEntry)
def get_history_entry(entry_id: int):
    entry = store.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return HistoryEntry(**entry)


@app.post("/history/{entry_id}/feedback")
def add_feedback(entry_id: int, req: FeedbackRequest):
    if not store.get_by_id(entry_id):
        raise HTTPException(status_code=404, detail="Entry not found")
    store.update_feedback(entry_id, req.feedback)
    return {"status": "ok"}


@app.delete("/history/{entry_id}")
def delete_entry(entry_id: int):
    if not store.get_by_id(entry_id):
        raise HTTPException(status_code=404, detail="Entry not found")
    store.delete_entry(entry_id)
    return {"status": "deleted"}


@app.get("/export")
def export_history(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    classification: str = "",
    conversation_id: str = "",
):
    entries = store.get_all(
        limit=500, classification=classification,
        conversation_id=conversation_id,
    )

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "conversation_id", "timestamp", "query", "classification",
            "tools_used", "response", "validated", "execution_time", "feedback",
        ])
        for e in entries:
            writer.writerow([
                e["id"], e["conversation_id"], e["timestamp"], e["query"],
                e["classification"], json.dumps(e["tools_used"]),
                e["response"], e["validated"], e["execution_time"], e.get("feedback", ""),
            ])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=history.csv"},
        )

    return entries


@app.get("/stats")
def get_stats():
    entries = store.get_all(limit=1000)
    total = len(entries)
    if total == 0:
        return {"total": 0}
    classified = sum(1 for e in entries if e["classification"] != "escalate")
    validated = sum(1 for e in entries if e.get("validated"))
    avg_time = sum(e["execution_time"] for e in entries if e["execution_time"]) / total
    by_category = {}
    for e in entries:
        cat = e["classification"]
        by_category[cat] = by_category.get(cat, 0) + 1
    positive = sum(1 for e in entries if e.get("feedback") == 1)
    negative = sum(1 for e in entries if e.get("feedback") == -1)
    return {
        "total": total,
        "classified": classified,
        "validated": validated,
        "avg_execution_time": round(avg_time, 2),
        "by_category": by_category,
        "feedback_positive": positive,
        "feedback_negative": negative,
    }
