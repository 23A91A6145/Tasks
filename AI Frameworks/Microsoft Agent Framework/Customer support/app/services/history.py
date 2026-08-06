import os
import json
from datetime import datetime
from app.config import HISTORY_DIR

def save_history(session_id: str, messages: list, metadata: dict) -> None:
    """Saves the conversation history and metadata for a session to a JSON file."""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    
    # Format messages to JSON serializable structures
    serializable_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            serializable_messages.append(msg)
            continue
            
        # If it's a Message object from agent_framework
        contents_repr = []
        for c in (msg.contents or []):
            if isinstance(c, str):
                contents_repr.append({"type": "text", "text": c})
            elif hasattr(c, "to_dict"):
                contents_repr.append(c.to_dict())
            elif isinstance(c, dict):
                contents_repr.append(c)
            else:
                contents_repr.append({"type": "unknown", "raw": str(c)})
                
        serializable_messages.append({
            "role": msg.role,
            "author": msg.author_name,
            "contents": contents_repr
        })

    data = {
        "session_id": session_id,
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "metadata": metadata,
        "messages": serializable_messages
    }
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_history(session_id: str) -> dict:
    """Loads history for a given session. Returns default structure if not found."""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if not os.path.exists(filepath):
        return {
            "session_id": session_id,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "active_agent": "Triage",
                "status": "Online",
                "resolved": False,
                "escalated": False
            },
            "messages": []
        }
        
    with open(filepath, "r") as f:
        return json.load(f)

def list_sessions() -> list[str]:
    """Returns a list of all active or saved session IDs."""
    sessions = []
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith(".json"):
            sessions.append(filename[:-5])
    return sorted(sessions)
