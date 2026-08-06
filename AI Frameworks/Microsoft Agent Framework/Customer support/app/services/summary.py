import json
import logging
from agent_framework import Message
from app.config import get_chat_client
from app.services.history import load_history
from app.services.logger import log_error

def generate_heuristic_summary(session_id: str, history_data: dict) -> dict:
    """Generates a summary using heuristics based on history data and metadata."""
    metadata = history_data.get("metadata", {})
    messages = history_data.get("messages", [])
    
    # Calculate turns
    user_turns = sum(1 for m in messages if m.get("role") == "user")
    
    # Check resolution status
    resolution = "In Progress"
    if metadata.get("resolved"):
        resolution = "Resolved"
    elif metadata.get("escalated"):
        resolution = "Escalated"
        
    # Check assigned agent
    assigned_agent = metadata.get("active_agent", "Triage")
    
    # Determine category based on which agents were visited
    visited_agents = set()
    for m in messages:
        author = m.get("author")
        if author in ["Triage", "Billing", "Technical", "General"]:
            visited_agents.add(author)
            
    visited_agents.discard("Triage") # focus on specialists
    if not visited_agents:
        category = "General"
    elif len(visited_agents) == 1:
        category = list(visited_agents)[0]
    else:
        category = "Multi-topic"
        
    # Heuristic for issue description based on the first user message
    user_messages = [m for m in messages if m.get("role") == "user"]
    if user_messages:
        first_msg = ""
        for c in user_messages[0].get("contents", []):
            if isinstance(c, dict) and c.get("type") == "text":
                first_msg = c.get("text", "")
                break
        issue = first_msg[:60] + "..." if len(first_msg) > 60 else first_msg
    else:
        issue = "No customer messages found."
        
    # Heuristic for priority: if user mentioned crash, login denied, server error, or urgent, set High.
    priority = "Low"
    crash_keywords = ["crash", "fail", "error", "reset", "denied", "broken", "urgent", "login", "payment failed", "failed"]
    full_text = " ".join([c.get("text", "").lower() for m in messages for c in m.get("contents", []) if isinstance(c, dict) and c.get("type") == "text"])
    
    if any(kw in full_text for kw in crash_keywords):
        priority = "High"
    elif user_turns > 3:
        priority = "Medium"
        
    return {
        "issue": issue or "General support query.",
        "category": category,
        "priority": priority,
        "assigned_agent": assigned_agent,
        "resolution": resolution,
        "turns": user_turns
    }

async def generate_ticket_summary(session_id: str) -> dict:
    """Generates a summary of the ticket using the LLM with a fallback to heuristics."""
    history_data = load_history(session_id)
    heuristic = generate_heuristic_summary(session_id, history_data)
    
    messages = history_data.get("messages", [])
    if not messages:
        return heuristic
        
    # Format the transcript for the LLM
    transcript = []
    for m in messages:
        role = m.get("role", "").upper()
        author = m.get("author", role)
        text_parts = []
        for c in m.get("contents", []):
            if isinstance(c, dict) and c.get("type") == "text":
                text_parts.append(c.get("text", ""))
        text = "\n".join(text_parts)
        if text:
            transcript.append(f"{author} ({role}): {text}")
        
    formatted_transcript = "\n".join(transcript)
    
    prompt = (
        "You are a Ticket Summarization Assistant.\n"
        "Analyze the support conversation transcript below and output a JSON object summarizing the ticket.\n"
        "Your output must be a raw JSON object and nothing else. Do not wrap it in markdown code blocks or add explanations.\n"
        "Required JSON schema:\n"
        "{\n"
        '  "issue": "A 1-sentence summary of the customer\'s core problem.",\n'
        '  "category": "Billing" or "Technical" or "General" or "Multi-topic",\n'
        '  "priority": "Low" or "Medium" or "High",\n'
        '  "assigned_agent": "Triage" or "Billing" or "Technical" or "General",\n'
        '  "resolution": "Resolved" or "Escalated" or "In Progress"\n'
        "}\n\n"
        f"Transcript:\n{formatted_transcript}\n"
    )
    
    try:
        client = get_chat_client()
        msg = Message(role="user", contents=[prompt])
        
        # We run the async call
        response = await client.get_response([msg])
        response_text = response.text.strip()
        
        # Clean any accidental markdown wrapping from LLM
        if response_text.startswith("```"):
            lines = response_text.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                response_text = "\n".join(lines[1:-1])
                
        data = json.loads(response_text)
        
        # Merge with heuristic turn count and ensure fields
        summary = {
            "issue": data.get("issue", heuristic["issue"]),
            "category": data.get("category", heuristic["category"]),
            "priority": data.get("priority", heuristic["priority"]),
            "assigned_agent": data.get("assigned_agent", heuristic["assigned_agent"]),
            "resolution": data.get("resolution", heuristic["resolution"]),
            "turns": heuristic["turns"]
        }
        return summary
    except Exception as e:
        log_error(f"Failed to generate LLM summary for {session_id}, falling back to heuristics. Error: {str(e)}")
        return heuristic
