import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class ChatHistory:
    def __init__(self, storage_dir: str = "data/sessions"):
        self.storage = Path(storage_dir)
        self.storage.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        return self.storage / f"{session_id}.json"

    def save(self, session_id: str, messages: List[Dict]) -> None:
        data = {
            "session_id": session_id,
            "updated_at": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": messages,
        }
        self._session_path(session_id).write_text(json.dumps(data, indent=2))

    def load(self, session_id: str) -> List[Dict]:
        path = self._session_path(session_id)
        if not path.exists():
            return []
        data = json.loads(path.read_text())
        return data.get("messages", [])

    def list_sessions(self) -> List[Dict]:
        sessions = []
        for path in sorted(self.storage.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            data = json.loads(path.read_text())
            sessions.append({
                "id": data.get("session_id", path.stem),
                "count": data.get("message_count", 0),
                "updated": data.get("updated_at", ""),
            })
        return sessions

    def delete(self, session_id: str) -> None:
        self._session_path(session_id).unlink(missing_ok=True)

    def export_markdown(self, messages: List[Dict]) -> str:
        lines = [f"# Chat Export — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
        for msg in messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            ts = msg.get("timestamp", "")
            lines.append(f"## {role}")
            if ts:
                lines.append(f"*{ts}*")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)

    def export_json(self, messages: List[Dict]) -> str:
        return json.dumps({
            "exported_at": datetime.now().isoformat(),
            "messages": messages,
        }, indent=2)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    @staticmethod
    def compute_stats(messages: List[Dict]) -> Dict:
        total = len(messages)
        user_msgs = sum(1 for m in messages if m["role"] == "user")
        assistant_msgs = sum(1 for m in messages if m["role"] == "assistant")
        all_text = " ".join(m.get("content", "") for m in messages)
        estimated_tokens = ChatHistory.estimate_tokens(all_text)

        first_ts = None
        last_ts = None
        for m in messages:
            ts = m.get("timestamp", "")
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

        return {
            "total": total,
            "user": user_msgs,
            "assistant": assistant_msgs,
            "estimated_tokens": estimated_tokens,
            "first_message": first_ts or "",
            "last_message": last_ts or "",
        }
