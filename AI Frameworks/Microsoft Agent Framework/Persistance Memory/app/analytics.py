"""
Analytics Engine for Persistent Memory Chat CLI (Volume 3).
Calculates token usage, memory density, response latency, and system-wide storage stats.
"""

from typing import Dict, Any, List
from pathlib import Path
from app.history import FileHistoryProvider

class AnalyticsEngine:
    """Calculates detailed session and system-wide performance & token metrics."""

    def __init__(self, history_provider: FileHistoryProvider):
        self.provider = history_provider

    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Calculates deep analytics for a specific session."""
        stats = self.provider.get_session_stats(session_id)
        messages = self.provider.load_history(session_id)

        total_msgs = stats["total_messages"]
        total_tokens = stats["total_tokens"]

        user_tokens = sum(m.get("tokens", 0) for m in messages if m.get("role") == "user")
        assistant_tokens = sum(m.get("tokens", 0) for m in messages if m.get("role") == "assistant")

        avg_tokens_per_msg = round(total_tokens / total_msgs, 1) if total_msgs > 0 else 0.0
        facts_count = len(stats.get("facts", {}))

        return {
            "session_id": session_id,
            "title": stats.get("title", session_id),
            "total_messages": total_msgs,
            "user_messages": stats["user_messages"],
            "assistant_messages": stats["assistant_messages"],
            "total_tokens": total_tokens,
            "user_tokens": user_tokens,
            "assistant_tokens": assistant_tokens,
            "avg_tokens_per_msg": avg_tokens_per_msg,
            "facts_count": facts_count,
            "disk_size_kb": stats["file_size_kb"],
            "created_at": stats.get("created_at", ""),
            "updated_at": stats.get("updated_at", ""),
            "file_path": stats["file_path"],
        }

    def get_system_analytics(self) -> Dict[str, Any]:
        """Calculates aggregated metrics across all persistent sessions."""
        all_sessions = self.provider.list_sessions()
        total_sessions = len(all_sessions)
        
        grand_total_msgs = 0
        grand_total_tokens = 0
        grand_total_facts = 0
        grand_total_size_kb = 0.0

        session_summaries = []

        for s in all_sessions:
            sid = s["id"]
            s_analytics = self.get_session_analytics(sid)
            grand_total_msgs += s_analytics["total_messages"]
            grand_total_tokens += s_analytics["total_tokens"]
            grand_total_facts += s_analytics["facts_count"]
            grand_total_size_kb += s_analytics["disk_size_kb"]

            session_summaries.append({
                "id": sid,
                "title": s_analytics["title"],
                "messages": s_analytics["total_messages"],
                "tokens": s_analytics["total_tokens"],
                "facts": s_analytics["facts_count"],
                "size_kb": s_analytics["disk_size_kb"],
                "updated_at": s_analytics["updated_at"],
            })

        return {
            "total_sessions": total_sessions,
            "grand_total_messages": grand_total_msgs,
            "grand_total_tokens": grand_total_tokens,
            "grand_total_facts": grand_total_facts,
            "grand_total_disk_kb": round(grand_total_size_kb, 2),
            "sessions": session_summaries,
        }
