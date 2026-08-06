import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from agent_framework import InMemoryCheckpointStorage, AgentResponse
from agent_framework.orchestrations import HandoffAgentUserRequest

from app.workflows.handoff import create_handoff_workflow
from app.services.history import load_history, save_history, list_sessions
from app.services.analytics import get_analytics
from app.services.routing import list_agents_info
from app.services.logger import log_chat, log_routing, log_error
from app.config import CHECKPOINTS_DIR, RuntimeConfig

router = APIRouter()

# Global in-memory checkpoint storage for highly reliable, fast stateless executions
checkpoint_storage = InMemoryCheckpointStorage()

class ChatRequest(BaseModel):
    message: str
    session_id: str

class SessionRequest(BaseModel):
    session_id: str | None = None

class SettingsRequest(BaseModel):
    provider: str
    ollama_model: str | None = None
    openai_model: str | None = None
    groq_model: str | None = None
    gemini_model: str | None = None

class ResolveRequest(BaseModel):
    session_id: str

@router.post("/chat")
async def chat(req: ChatRequest):
    """Sends a message to the AI Support workflow and retrieves the response."""
    session_id = req.session_id.strip()
    message = req.message.strip()

    if not session_id or not message:
        raise HTTPException(status_code=400, detail="session_id and message are required.")

    # Load session history and state
    session_data = load_history(session_id)
    metadata = session_data.get("metadata", {
        "active_agent": "Triage",
        "status": "Online",
        "resolved": False,
        "escalated": False
    })
    messages = session_data.get("messages", [])

    if metadata.get("resolved") or metadata.get("escalated"):
        return {
            "output_messages": [{"author": "System", "text": "This ticket has been resolved or escalated. Run /restart or transfer to re-open."}],
            "metadata": metadata,
            "session_id": session_id
        }

    # Retrieve checkpoint ID and pending request ID from metadata
    checkpoint_id = metadata.get("checkpoint_id")
    pending_request_id = metadata.get("pending_request_id")

    # Log user message
    log_chat(session_id, "user", "Customer", message)

    # Append user message to history with current timestamp
    messages.append({
        "role": "user",
        "author": "Customer",
        "contents": [{"type": "text", "text": message}],
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    })

    new_request_id = None
    output_messages = []

    # Parse resulting events helper
    def process_result_events(result):
        nonlocal new_request_id
        for event in result:
            if event.type == "handoff_sent" and event.data:
                metadata["active_agent"] = event.data.target
                log_routing(session_id, event.data.source, event.data.target)
            elif event.type == "request_info":
                new_request_id = event.request_id
            elif event.type == "output" and event.data:
                if isinstance(event.data, AgentResponse):
                    for msg in event.data.messages:
                        text_parts = []
                        for c in (msg.contents or []):
                            if hasattr(c, "type") and c.type == "text" and c.text:
                                text_parts.append(c.text)
                        final_text = "\n".join(text_parts)
                        if final_text:
                            messages.append({
                                "role": "assistant",
                                "author": msg.author_name,
                                "contents": [{"type": "text", "text": final_text}],
                                "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
                            })
                            output_messages.append({
                                "author": msg.author_name,
                                "text": final_text
                            })
                            log_chat(session_id, "assistant", msg.author_name, final_text)

    # Execute workflow using global in-memory storage with automated fallback
    resumed = False
    if checkpoint_id and pending_request_id:
        try:
            workflow = create_handoff_workflow(checkpoint_storage=checkpoint_storage)
            user_messages = HandoffAgentUserRequest.create_response(message)
            run_coro = workflow.run(
                responses={pending_request_id: user_messages},
                checkpoint_id=checkpoint_id
            )
            result = await run_coro
            process_result_events(result)
            resumed = True
        except Exception as e:
            log_error(f"In-memory checkpoint resumption failed for API session {session_id}, falling back to fresh run: {e}")
            metadata["checkpoint_id"] = None
            metadata["pending_request_id"] = None
            checkpoint_id = None
            pending_request_id = None

    if not resumed:
        try:
            workflow = create_handoff_workflow(checkpoint_storage=checkpoint_storage)
            run_coro = workflow.run(message=message)
            result = await run_coro
            process_result_events(result)
        except Exception as e:
            log_error(f"Error executing workflow for session {session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

    # Fetch the latest checkpoint created from storage
    checkpoint_ids = await checkpoint_storage.list_checkpoint_ids(workflow_name="customer_support")
    latest_checkpoint = checkpoint_ids[-1] if checkpoint_ids else None

    # Update metadata with checkpoints
    metadata["checkpoint_id"] = latest_checkpoint
    metadata["pending_request_id"] = new_request_id

    # Save session back to file
    save_history(session_id, messages, metadata)

    return {
        "output_messages": output_messages,
        "metadata": metadata,
        "session_id": session_id
    }

@router.get("/agents")
def get_agents():
    """Lists available agents, roles, descriptions, and tools."""
    return list_agents_info()

@router.get("/history")
def get_history(session_id: str):
    """Retrieves full conversation history and metadata for a specific session."""
    return load_history(session_id)

@router.get("/status")
def get_status():
    """Returns analytics data, system config, and list of sessions."""
    return {
        "provider": RuntimeConfig.LLM_PROVIDER,
        "sessions": list_sessions(),
        "analytics": get_analytics(),
        "models": {
            "ollama": RuntimeConfig.OLLAMA_MODEL,
            "openai": RuntimeConfig.OPENAI_MODEL,
            "groq": RuntimeConfig.GROQ_MODEL,
            "gemini": RuntimeConfig.GEMINI_MODEL
        }
    }

@router.post("/session")
def create_session(req: SessionRequest):
    """Creates a new unique session or registers a chosen custom session ID."""
    session_id = (req.session_id or "").strip()
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    # Load session history or initialize default state
    history = load_history(session_id)
    
    # Save the initial session state to disk immediately
    save_history(session_id, history.get("messages", []), history.get("metadata", {}))
    
    return {
        "session_id": session_id,
        "status": "Initialized",
        "metadata": history.get("metadata")
    }

@router.post("/handoff")
async def force_handoff(session_id: str, target_agent: str):
    """Manually flags a session to transfer control to a chosen specialist agent."""
    session_data = load_history(session_id)
    metadata = session_data["metadata"]
    source_agent = metadata.get("active_agent", "Triage")
    metadata["active_agent"] = target_agent
    
    # Clear checkpoint fields in metadata to force a fresh run for the new agent
    metadata["checkpoint_id"] = None
    metadata["pending_request_id"] = None
    
    # Reset resolved and escalated flags when manually transferring control or restarting
    metadata["resolved"] = False
    metadata["escalated"] = False
    metadata["status"] = "Online"
    if "summary" in metadata:
        metadata.pop("summary")
                
    save_history(session_id, session_data["messages"], metadata)
    log_routing(session_id, f"Manual_Force_{source_agent}", target_agent)
    
    return {"session_id": session_id, "active_agent": target_agent, "status": "Handoff Forced"}

class RestartRequest(BaseModel):
    session_id: str

@router.post("/restart")
def restart_session(req: RestartRequest):
    """Resets conversation history and wipes checkpoints to start fresh."""
    session_id = req.session_id.strip()
    
    metadata = {
        "active_agent": "Triage",
        "status": "Online",
        "resolved": False,
        "escalated": False,
        "checkpoint_id": None,
        "pending_request_id": None
    }
    
    save_history(session_id, [], metadata)
    log_routing(session_id, "System_Restart", "Triage")
    return {"session_id": session_id, "status": "Restarted"}


@router.post("/settings")
def update_settings(req: SettingsRequest):
    """Updates provider and model config at runtime."""
    prov = req.provider.strip().lower()
    if prov not in ["ollama", "openai", "groq", "gemini"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Must be ollama, openai, groq, or gemini.")
    
    RuntimeConfig.LLM_PROVIDER = prov
    if req.ollama_model:
        RuntimeConfig.OLLAMA_MODEL = req.ollama_model
    if req.openai_model:
        RuntimeConfig.OPENAI_MODEL = req.openai_model
    if req.groq_model:
        RuntimeConfig.GROQ_MODEL = req.groq_model
    if req.gemini_model:
        RuntimeConfig.GEMINI_MODEL = req.gemini_model
        
    return {
        "status": "Settings updated",
        "provider": RuntimeConfig.LLM_PROVIDER,
        "models": {
            "ollama": RuntimeConfig.OLLAMA_MODEL,
            "openai": RuntimeConfig.OPENAI_MODEL,
            "groq": RuntimeConfig.GROQ_MODEL,
            "gemini": RuntimeConfig.GEMINI_MODEL
        }
    }

@router.get("/summary")
async def get_summary(session_id: str):
    """Generates or retrieves a ticket summary for a session."""
    session_data = load_history(session_id)
    metadata = session_data.get("metadata", {})
    
    if "summary" in metadata:
        return metadata["summary"]
        
    from app.services.summary import generate_ticket_summary
    summary = await generate_ticket_summary(session_id)
    
    metadata["summary"] = summary
    save_history(session_id, session_data.get("messages", []), metadata)
    return summary

@router.post("/resolve")
async def resolve(req: ResolveRequest):
    """Marks a session as resolved and generates/saves a ticket summary."""
    session_id = req.session_id.strip()
    session_data = load_history(session_id)
    metadata = session_data.get("metadata", {})
    metadata["resolved"] = True
    metadata["status"] = "Resolved"
    
    from app.services.summary import generate_ticket_summary
    summary = await generate_ticket_summary(session_id)
    metadata["summary"] = summary
    
    save_history(session_id, session_data.get("messages", []), metadata)
    return {
        "session_id": session_id,
        "status": "Resolved",
        "summary": summary
    }

@router.get("/export", response_class=PlainTextResponse)
def export_session(session_id: str):
    """Generates and returns a readable Markdown transcript of the session."""
    session_data = load_history(session_id)
    if not session_data or not session_data.get("messages"):
        raise HTTPException(status_code=404, detail="Session not found or empty.")
    
    metadata = session_data.get("metadata", {})
    messages = session_data.get("messages", [])
    
    md = []
    md.append(f"# AI Customer Support Transcript - Session: {session_id}")
    md.append(f"- **Timestamp**: {session_data.get('last_updated', 'N/A')}")
    md.append(f"- **LLM Provider**: {RuntimeConfig.LLM_PROVIDER.upper()}")
    md.append(f"- **Final Active Agent**: {metadata.get('active_agent', 'Triage')}")
    md.append(f"- **Status**: {'Resolved' if metadata.get('resolved') else ('Escalated' if metadata.get('escalated') else 'Active')}")
    
    # If summary exists, append it to transcript header
    if "summary" in metadata:
        s = metadata["summary"]
        md.append("\n## Ticket Summary")
        md.append(f"- **Core Issue**: {s.get('issue')}")
        md.append(f"- **Category**: {s.get('category')}")
        md.append(f"- **Priority**: {s.get('priority')}")
        md.append(f"- **Turns**: {s.get('turns')}")
        
    md.append("\n---\n")
    
    for msg in messages:
        role = msg.get("role", "").upper()
        author = msg.get("author", "Unknown")
        
        text_parts = []
        for c in msg.get("contents", []):
            if c.get("type") == "text":
                text_parts.append(c.get("text", ""))
            elif c.get("type") == "function_call":
                text_parts.append(f"*System Tool Call: {c.get('name')}({c.get('arguments')})*")
            elif c.get("type") == "function_result":
                text_parts.append(f"*System Tool Result: {c.get('result')}*")
                
        text = "\n".join(text_parts)
        if role == "USER":
            md.append(f"### 👤 Customer\n{text}\n")
        else:
            md.append(f"### 🤖 {author} ({role.title()})\n{text}\n")
            
    return "\n".join(md)
