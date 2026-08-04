"""
Memory Compaction and Sliding Window Summarizer Engine for Volume 4.
Summarizes older conversation turns to prevent token bloat while retaining deep memory context.
"""

from typing import List, Dict, Any, Tuple
from app.utils import estimate_tokens

class MemoryCompactor:
    """
    Compacts session context when message turns exceed max_context limits.
    Compresses older turns into a concise persistent memory summary.
    """

    @staticmethod
    def summarize_messages(messages: List[Dict[str, Any]]) -> str:
        """Generates a concise bulleted summary of message turns."""
        if not messages:
            return ""

        summary_lines = []
        for m in messages:
            role = m.get("role", "").upper()
            content = m.get("content", "").strip()
            # Truncate content snippet for summary
            snippet = content[:60] + "..." if len(content) > 60 else content
            summary_lines.append(f"[{role}]: {snippet}")

        return "Past Conversation Summary:\n" + "\n".join(summary_lines)

    @classmethod
    def process_sliding_window(
        cls,
        messages: List[Dict[str, Any]],
        max_context: int,
        existing_summary: str = ""
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Processes sliding context window:
        If total messages exceed max_context, splits older messages out,
        summarizes them, and returns (recent_messages, updated_summary).
        """
        if len(messages) <= max_context:
            return messages, existing_summary

        # Split older overflow messages and recent messages
        overflow_count = len(messages) - max_context
        overflow_msgs = messages[:overflow_count]
        recent_msgs = messages[overflow_count:]

        new_summary_chunk = cls.summarize_messages(overflow_msgs)
        
        if existing_summary:
            updated_summary = f"{existing_summary}\n\n{new_summary_chunk}"
        else:
            updated_summary = new_summary_chunk

        return recent_msgs, updated_summary
