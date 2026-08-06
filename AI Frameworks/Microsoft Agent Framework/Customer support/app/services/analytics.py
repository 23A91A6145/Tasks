import os
import json
from datetime import datetime
from app.config import HISTORY_DIR

def parse_timestamp(ts_str: str) -> datetime | None:
    """Safely parses an ISO timestamp string to a datetime object."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return None

def get_analytics() -> dict:
    """Aggregates detailed analytics across all customer support sessions."""
    total_sessions = 0
    resolved_tickets = 0
    escalated_tickets = 0
    total_messages = 0
    agent_usage = {
        "Triage": 0,
        "Billing": 0,
        "Technical": 0,
        "General": 0
    }
    
    session_times = []
    response_times = []
    
    # Read all sessions
    if os.path.exists(HISTORY_DIR):
        for filename in os.listdir(HISTORY_DIR):
            if not filename.endswith(".json") or filename == "checkpoints":
                continue
                
            total_sessions += 1
            filepath = os.path.join(HISTORY_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    
                metadata = data.get("metadata", {})
                if metadata.get("resolved"):
                    resolved_tickets += 1
                if metadata.get("escalated"):
                    escalated_tickets += 1
                    
                messages = data.get("messages", [])
                total_messages += len(messages)
                
                # Analyze message timestamps for session duration and response latency
                message_timestamps = []
                for msg in messages:
                    # Increment agent usage counts
                    author = msg.get("author")
                    if author in agent_usage:
                        agent_usage[author] += 1
                    
                    # Capture timestamp
                    ts = parse_timestamp(msg.get("timestamp"))
                    if ts:
                        message_timestamps.append((ts, msg.get("role")))
                
                # Calculate session duration
                if len(message_timestamps) >= 2:
                    start_time = message_timestamps[0][0]
                    end_time = message_timestamps[-1][0]
                    duration = (end_time - start_time).total_seconds()
                    if duration >= 0:
                        session_times.append(duration)
                
                # Calculate response times (user query to agent reply latency)
                for i in range(len(message_timestamps) - 1):
                    curr_ts, curr_role = message_timestamps[i]
                    next_ts, next_role = message_timestamps[i+1]
                    if curr_role == "user" and next_role == "assistant":
                        latency = (next_ts - curr_ts).total_seconds()
                        if latency >= 0:
                            response_times.append(latency)
            except Exception:
                pass # skip corrupted records
                
    resolution_rate = (resolved_tickets / total_sessions * 100) if total_sessions > 0 else 0.0
    avg_session_time = (sum(session_times) / len(session_times)) if session_times else 0.0
    avg_response_time = (sum(response_times) / len(response_times)) if response_times else 0.0
    
    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "resolved_tickets": resolved_tickets,
        "escalated_tickets": escalated_tickets,
        "resolution_rate": f"{resolution_rate:.1f}%",
        "agent_conversations": agent_usage,
        "avg_session_time_seconds": round(avg_session_time, 1),
        "avg_response_time_seconds": round(avg_response_time, 1),
        "avg_session_time_str": format_duration(avg_session_time),
        "avg_response_time_str": format_duration(avg_response_time)
    }

def format_duration(seconds: float) -> str:
    """Formats a duration in seconds to a human-readable string."""
    if seconds <= 0:
        return "N/A"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
