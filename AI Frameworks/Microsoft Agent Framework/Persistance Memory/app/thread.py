"""
AgentThread implementation for Volume 4 Persistent Memory System.
Handles session state, system instructions, memory fact injection, persistent summary, and context sliding windows.
"""

from typing import List, Dict, Any, Optional
from app.memory import PersistentMemoryManager

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are a stateful AI assistant powered by Microsoft Agent Framework concepts. "
    "Maintain helpful, accurate, concise responses while recalling persistent user context and memory summaries."
)

class AgentThread:
    """
    AgentThread encapsulates stateful session execution.
    Manages system instructions, restored memory facts, persistent memory summaries, and sliding context windows.
    """

    def __init__(
        self,
        session_id: str,
        memory_manager: PersistentMemoryManager,
        max_context: int = 20,
        system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION
    ):
        self.session_id = session_id
        self.memory_manager = memory_manager
        self.max_context = max_context
        self.system_instruction = system_instruction
        self.messages: List[Dict[str, Any]] = []
        self.resume_thread()

    def resume_thread(self) -> None:
        """Resumes thread by loading history from persistent memory."""
        self.messages = self.memory_manager.load_session_history(self.session_id)

    def switch_session(self, new_session_id: str) -> None:
        """Switches current thread to another session ID and loads its memory."""
        self.session_id = new_session_id
        self.resume_thread()

    def add_user_message(self, content: str) -> Dict[str, Any]:
        """Appends user message to persistent memory and active thread state."""
        record = self.memory_manager.save_user_message(self.session_id, content)
        self.messages.append(record)
        return record

    def add_assistant_message(self, content: str, model: str) -> Dict[str, Any]:
        """Appends assistant message to persistent memory and active thread state."""
        record = self.memory_manager.save_assistant_message(self.session_id, content, model)
        self.messages.append(record)
        return record

    def get_extracted_facts(self) -> Dict[str, str]:
        """Gets all extracted facts stored in session metadata."""
        return self.memory_manager.get_extracted_facts(self.session_id)

    def get_session_summary(self) -> str:
        """Gets persistent memory summary stored in session metadata."""
        return self.memory_manager.get_session_summary(self.session_id)

    def get_context(self) -> List[Dict[str, str]]:
        """
        Returns bounded sliding window of context for LLM prompt payload,
        prefixed with System Instructions, Extracted Memory Facts, and Persistent Memory Summary.
        """
        # Process sliding window compaction first to calculate/update memory summary
        recent_msgs, updated_summary = self.memory_manager.apply_sliding_window_compaction(
            session_id=self.session_id,
            max_context=self.max_context
        )

        context: List[Dict[str, str]] = []

        # System Instruction Header
        system_text = self.system_instruction

        # Injected Memory Facts
        facts = self.get_extracted_facts()
        if facts:
            fact_lines = [f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in facts.items()]
            system_text += "\n\n[Persistent User Facts Memory]:\n" + "\n".join(fact_lines)

        # Injected Persistent Memory Summary
        if updated_summary:
            system_text += f"\n\n[Persistent Memory Summary (Older Turns)]:\n{updated_summary}"

        context.append({"role": "system", "content": system_text})

        for m in recent_msgs:
            context.append({"role": m["role"], "content": m["content"]})

        return context

    def compact(self) -> int:
        """Compacts session storage file."""
        count = self.memory_manager.compact(self.session_id)
        self.resume_thread()
        return count

    def clear(self) -> None:
        """Clears thread memory and resets message list."""
        self.memory_manager.clear_session(self.session_id)
        self.messages = []

    @property
    def title(self) -> str:
        """Returns session title."""
        stats = self.memory_manager.get_stats(self.session_id)
        return stats.get("title", self.session_id)
