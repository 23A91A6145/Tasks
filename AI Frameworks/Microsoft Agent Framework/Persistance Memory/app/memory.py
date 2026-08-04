"""
Persistent Memory Manager Facade with Automatic Semantic Fact Extraction & Memory Summarization (Volume 4).
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from app.history import FileHistoryProvider
from app.compaction import MemoryCompactor

class PersistentMemoryManager:
    """
    High-level memory manager handling session history storage, keyword searching,
    history compaction, automatic user fact extraction, and sliding window summarization.
    """

    def __init__(self, history_dir: Path):
        self.provider = FileHistoryProvider(history_dir)

    def load_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves persistent message history for a given session."""
        return self.provider.load_history(session_id)

    def extract_facts_from_text(self, text: str) -> Dict[str, str]:
        """Parses user text turns and extracts key semantic facts."""
        facts: Dict[str, str] = {}

        name_match = re.search(r"\bmy name is ([A-Za-z0-9_\- ]+?)(?:\.|$|,| and)", text, re.IGNORECASE)
        if name_match:
            facts["name"] = name_match.group(1).strip()

        role_match = re.search(r"\bi am (?:a|an) ([A-Za-z0-9_\- ]+?)(?:\.|$|,| working)", text, re.IGNORECASE)
        if role_match:
            facts["role"] = role_match.group(1).strip()

        tech_match = re.search(r"\b(?:my tech stack is|i work with|i use) ([A-Za-z0-9_\-\.\, ]+?)(?:\.|$)", text, re.IGNORECASE)
        if tech_match:
            facts["tech_stack"] = tech_match.group(1).strip()

        loc_match = re.search(r"\bi (?:live in|am from|am located in) ([A-Za-z0-9_\- ]+?)(?:\.|$|,)", text, re.IGNORECASE)
        if loc_match:
            facts["location"] = loc_match.group(1).strip()

        pref_match = re.search(r"\bi prefer ([A-Za-z0-9_\- ]+?)(?:\.|$|,)", text, re.IGNORECASE)
        if pref_match:
            facts["preference"] = pref_match.group(1).strip()

        return facts

    def save_user_message(self, session_id: str, content: str) -> Dict[str, Any]:
        """Saves user message turn and automatically extracts & persists new user memory facts."""
        record = self.provider.append_message(session_id, role="user", content=content)
        
        extracted_facts = self.extract_facts_from_text(content)
        if extracted_facts:
            self.provider.update_session_meta(session_id, facts=extracted_facts)

        return record

    def save_assistant_message(self, session_id: str, content: str, model: str) -> Dict[str, Any]:
        """Saves assistant message turn to persistent storage."""
        return self.provider.append_message(session_id, role="assistant", content=content, model=model)

    def get_extracted_facts(self, session_id: str) -> Dict[str, str]:
        """Gets all extracted facts for a session."""
        meta = self.provider.get_session_meta(session_id)
        return meta.get("facts", {})

    def get_session_summary(self, session_id: str) -> str:
        """Gets stored persistent memory summary for a session."""
        meta = self.provider.get_session_meta(session_id)
        return meta.get("summary", "")

    def update_session_summary(self, session_id: str, summary: str) -> None:
        """Updates persistent memory summary for a session."""
        self.provider.update_session_meta(session_id, summary=summary)

    def apply_sliding_window_compaction(
        self,
        session_id: str,
        max_context: int
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Processes sliding window summarization for a session."""
        messages = self.load_session_history(session_id)
        existing_summary = self.get_session_summary(session_id)

        recent_msgs, updated_summary = MemoryCompactor.process_sliding_window(
            messages=messages,
            max_context=max_context,
            existing_summary=existing_summary
        )

        if updated_summary != existing_summary:
            self.update_session_summary(session_id, updated_summary)

        return recent_msgs, updated_summary

    def clear_session(self, session_id: str) -> bool:
        """Clears memory for a specific session."""
        return self.provider.clear_history(session_id)

    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """Lists all existing sessions with metadata."""
        return self.provider.list_sessions()

    def get_stats(self, session_id: str) -> Dict[str, Any]:
        """Returns statistics for current session memory."""
        return self.provider.get_session_stats(session_id)

    def compact(self, session_id: str) -> int:
        """Compacts and cleans history file for session."""
        return self.provider.compact_session(session_id)

    def search(self, query: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches memory for matching keyword query."""
        return self.provider.search_history(query, session_id)

    def export(
        self,
        session_id: str,
        export_format: str = "txt"
    ) -> Optional[Path]:
        """Exports session history to requested format."""
        return self.provider.export_history(session_id, export_format=export_format)

    def set_session_title(self, session_id: str, new_title: str) -> None:
        """Updates custom title for a session."""
        self.provider.update_session_meta(session_id, title=new_title)
