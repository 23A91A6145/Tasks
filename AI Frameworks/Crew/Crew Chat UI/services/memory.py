from typing import List, Dict


class ConversationMemory:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self, window: int = 6) -> str:
        recent = self.history[-window:]
        return "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in recent
        )

    def get_last_user_query(self) -> str:
        for msg in reversed(self.history):
            if msg["role"] == "user":
                return msg["content"]
        return ""

    def clear(self) -> None:
        self.history.clear()

    @property
    def count(self) -> int:
        return len(self.history)

    @property
    def is_empty(self) -> bool:
        return len(self.history) == 0
