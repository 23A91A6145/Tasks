"""
FileHistoryProvider and Session Indexer for Persistent Memory System.
Manages JSONL session storage, index tracking, compaction, searching, multi-format exports (TXT, MD, JSON, HTML),
session cloning, deletion, and manual fact mutation.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.utils import estimate_tokens, get_iso_timestamp

class FileHistoryProvider:
    """
    Persistent JSONL storage provider with index tracking, integrity checking,
    compaction, multi-session searching, multi-format exports, session cloning, and fact mutation.
    """

    def __init__(self, history_dir: Path):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.history_dir / "index.json"
        self._ensure_index()

    def _ensure_index(self) -> None:
        """Ensures index.json metadata file exists and is valid."""
        if not self.index_file.exists():
            self._save_index({})

    def _load_index(self) -> Dict[str, Any]:
        """Loads session index dictionary from index.json."""
        if not self.index_file.exists():
            return {}
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_index(self, index_data: Dict[str, Any]) -> None:
        """Saves session index dictionary to index.json."""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

    def _get_session_file(self, session_id: str) -> Path:
        """Returns clean file path for a session ID."""
        clean_id = "".join(c for c in session_id if c.isalnum() or c in ("_", "-"))
        if not clean_id:
            clean_id = "session_default"
        return self.history_dir / f"{clean_id}.jsonl"

    def load_history(self, session_id: str, role_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Loads message turns for a session from JSONL, optionally filtered by role."""
        file_path = self._get_session_file(session_id)
        messages: List[Dict[str, Any]] = []

        if not file_path.exists():
            return messages

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            record = json.loads(line)
                            if isinstance(record, dict) and "role" in record and "content" in record:
                                if role_filter:
                                    if record["role"].lower() == role_filter.lower():
                                        messages.append(record)
                                else:
                                    messages.append(record)
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass

        return messages

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        model: str = "system"
    ) -> Dict[str, Any]:
        """Appends a new message record to the session JSONL file and updates index.json."""
        file_path = self._get_session_file(session_id)
        tokens = estimate_tokens(content)
        timestamp = get_iso_timestamp()

        msg_data = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "tokens": tokens,
            "model": model,
        }

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg_data, ensure_ascii=False) + "\n")

        # Update index metadata
        index = self._load_index()
        sess_meta = index.get(session_id, {
            "id": session_id,
            "title": f"Session {session_id}",
            "created_at": timestamp,
            "facts": {},
            "summary": ""
        })

        if role == "user" and (sess_meta.get("title") == f"Session {session_id}" or not sess_meta.get("title")):
            snippet = content[:30].strip()
            sess_meta["title"] = snippet if len(content) <= 30 else f"{snippet}..."

        sess_meta["updated_at"] = timestamp
        sess_meta["message_count"] = len(self.load_history(session_id))
        index[session_id] = sess_meta
        self._save_index(index)

        return msg_data

    def get_session_meta(self, session_id: str) -> Dict[str, Any]:
        """Gets index metadata for a session."""
        index = self._load_index()
        if session_id in index:
            return index[session_id]
        return {
            "id": session_id,
            "title": f"Session {session_id}",
            "created_at": get_iso_timestamp(),
            "updated_at": get_iso_timestamp(),
            "message_count": len(self.load_history(session_id)),
            "facts": {},
            "summary": ""
        }

    def update_session_meta(
        self,
        session_id: str,
        title: Optional[str] = None,
        facts: Optional[Dict[str, str]] = None,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates metadata (title, facts, or memory summary) for a session in index.json."""
        index = self._load_index()
        meta = index.get(session_id, {
            "id": session_id,
            "title": f"Session {session_id}",
            "created_at": get_iso_timestamp(),
            "updated_at": get_iso_timestamp(),
            "message_count": len(self.load_history(session_id)),
            "facts": {},
            "summary": ""
        })

        if title is not None:
            meta["title"] = title
        if facts is not None:
            current_facts = meta.get("facts", {})
            current_facts.update(facts)
            meta["facts"] = current_facts
        if summary is not None:
            meta["summary"] = summary

        meta["updated_at"] = get_iso_timestamp()
        meta["message_count"] = len(self.load_history(session_id))
        index[session_id] = meta
        self._save_index(index)
        return meta

    def remove_fact(self, session_id: str, fact_key: str) -> bool:
        """Removes a specific fact key from session metadata."""
        index = self._load_index()
        if session_id in index and "facts" in index[session_id]:
            facts = index[session_id]["facts"]
            key_lower = fact_key.lower().strip()
            found_key = None
            for k in facts.keys():
                if k.lower() == key_lower:
                    found_key = k
                    break
            if found_key:
                del facts[found_key]
                index[session_id]["updated_at"] = get_iso_timestamp()
                self._save_index(index)
                return True
        return False

    def set_fact(self, session_id: str, fact_key: str, fact_value: str) -> None:
        """Manually sets or overrides a fact key in session metadata."""
        self.update_session_meta(session_id, facts={fact_key: fact_value})

    def clone_session(self, source_session_id: str, target_session_id: str) -> bool:
        """Clones an existing session history and metadata to a new session ID."""
        messages = self.load_history(source_session_id)
        if not messages:
            return False

        meta = self.get_session_meta(source_session_id)
        
        # Clear existing target if present
        self.clear_history(target_session_id)

        # Copy messages
        for m in messages:
            self.append_message(target_session_id, role=m["role"], content=m["content"], model=m.get("model", "cloned"))

        # Copy metadata facts & title
        self.update_session_meta(
            target_session_id,
            title=f"Clone of {meta.get('title', source_session_id)}",
            facts=meta.get("facts", {}),
            summary=meta.get("summary", "")
        )
        return True

    def clear_history(self, session_id: str) -> bool:
        """Deletes session JSONL history file and removes session from index.json."""
        file_path = self._get_session_file(session_id)
        index = self._load_index()
        
        if session_id in index:
            del index[session_id]
            self._save_index(index)

        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Returns list of all active session metadata dicts sorted by updated_at."""
        index = self._load_index()
        for p in self.history_dir.glob("*.jsonl"):
            sid = p.stem
            if sid not in index:
                msgs = self.load_history(sid)
                index[sid] = {
                    "id": sid,
                    "title": f"Session {sid}",
                    "created_at": get_iso_timestamp(),
                    "updated_at": get_iso_timestamp(),
                    "message_count": len(msgs),
                    "facts": {},
                    "summary": ""
                }
        self._save_index(index)
        
        session_list = list(index.values())
        session_list.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        return session_list

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Calculates detailed message, token, file size, fact, and summary statistics."""
        messages = self.load_history(session_id)
        file_path = self._get_session_file(session_id)
        file_size_kb = (file_path.stat().st_size / 1024.0) if file_path.exists() else 0.0

        meta = self.get_session_meta(session_id)
        total_tokens = sum(m.get("tokens", 0) for m in messages)
        user_msgs = sum(1 for m in messages if m.get("role") == "user")
        assistant_msgs = sum(1 for m in messages if m.get("role") == "assistant")

        return {
            "session_id": session_id,
            "title": meta.get("title", session_id),
            "total_messages": len(messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "total_tokens": total_tokens,
            "file_size_kb": round(file_size_kb, 2),
            "file_path": str(file_path),
            "created_at": meta.get("created_at", ""),
            "updated_at": meta.get("updated_at", ""),
            "facts": meta.get("facts", {}),
            "summary": meta.get("summary", "")
        }

    def compact_session(self, session_id: str) -> int:
        """Compacts session history file by removing invalid lines and re-writing clean JSONL."""
        messages = self.load_history(session_id)
        file_path = self._get_session_file(session_id)
        
        with open(file_path, "w", encoding="utf-8") as f:
            for m in messages:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")

        self.update_session_meta(session_id)
        return len(messages)

    def search_history(self, query: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches message contents across sessions for keyword query."""
        query_lower = query.lower().strip()
        results: List[Dict[str, Any]] = []

        target_sessions = [session_id] if session_id else [s["id"] for s in self.list_sessions()]

        for sid in target_sessions:
            msgs = self.load_history(sid)
            for m in msgs:
                content = m.get("content", "")
                if query_lower in content.lower():
                    results.append({
                        "session_id": sid,
                        "role": m.get("role"),
                        "timestamp": m.get("timestamp"),
                        "content": content,
                        "match_snippet": content[:80]
                    })
        return results

    def export_history(
        self,
        session_id: str,
        export_format: str = "txt",
        export_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Exports session history into requested format: 'txt', 'md', 'json', or 'html'.
        """
        messages = self.load_history(session_id)
        if not messages:
            return None

        meta = self.get_session_meta(session_id)
        target_dir = export_dir or self.history_dir
        fmt = export_format.lower().strip()

        if fmt == "json":
            export_file = target_dir / f"{session_id}_export.json"
            export_data = {
                "metadata": meta,
                "messages": messages
            }
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return export_file

        elif fmt == "html":
            export_file = target_dir / f"{session_id}_export.html"
            with open(export_file, "w", encoding="utf-8") as f:
                f.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n")
                f.write(f"<title>Chat Export - {meta.get('title', session_id)}</title>\n")
                f.write("<style>\n")
                f.write("body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }\n")
                f.write(".container { max-width: 800px; margin: 0 auto; }\n")
                f.write(".header { background: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px; }\n")
                f.write(".header h1 { margin: 0 0 10px 0; color: #38bdf8; font-size: 24px; }\n")
                f.write(".fact-card { background: #0f766e; padding: 10px 15px; border-radius: 6px; margin-top: 10px; font-size: 14px; }\n")
                f.write(".msg { margin-bottom: 15px; padding: 15px; border-radius: 8px; font-size: 15px; line-height: 1.5; }\n")
                f.write(".user { background: #1e293b; border-left: 4px solid #10b981; }\n")
                f.write(".assistant { background: #1e293b; border-left: 4px solid #38bdf8; }\n")
                f.write(".role { font-weight: bold; font-size: 12px; text-transform: uppercase; margin-bottom: 5px; opacity: 0.8; }\n")
                f.write(".time { font-size: 11px; color: #94a3b8; float: right; }\n")
                f.write("</style>\n</head>\n<body>\n<div class='container'>\n")
                f.write("<div class='header'>\n")
                f.write(f"<h1>🤖 {meta.get('title', session_id)}</h1>\n")
                f.write(f"<div>Session ID: <code>{session_id}</code> | Total Messages: {len(messages)}</div>\n")

                facts = meta.get("facts", {})
                if facts:
                    f.write("<div class='fact-card'><strong>🧠 Extracted Memory Facts:</strong><br>")
                    for k, v in facts.items():
                        f.write(f"• <strong>{k.capitalize()}:</strong> {v} &nbsp;&nbsp;")
                    f.write("</div>\n")

                f.write("</div>\n<div class='timeline'>\n")
                for m in messages:
                    cls = "user" if m.get("role") == "user" else "assistant"
                    f.write(f"<div class='msg {cls}'>\n")
                    f.write(f"<span class='time'>{m.get('timestamp')}</span>\n")
                    f.write(f"<div class='role'>{m.get('role')}</div>\n")
                    f.write(f"<div>{m.get('content')}</div>\n")
                    f.write("</div>\n")
                f.write("</div>\n</div>\n</body>\n</html>\n")
            return export_file

        elif fmt == "md":
            export_file = target_dir / f"{session_id}_export.md"
            with open(export_file, "w", encoding="utf-8") as f:
                f.write(f"# 📜 Session History Export: {meta.get('title', session_id)}\n\n")
                f.write(f"- **Session ID**: `{session_id}`\n")
                f.write(f"- **Created At**: `{meta.get('created_at')}`\n")
                f.write(f"- **Exported At**: `{get_iso_timestamp()}`\n")
                f.write(f"- **Total Messages**: {len(messages)}\n\n")
                
                facts = meta.get("facts", {})
                if facts:
                    f.write("## 🧠 Extracted User Facts Memory\n")
                    for k, v in facts.items():
                        f.write(f"- **{k.capitalize()}**: {v}\n")
                    f.write("\n")

                if meta.get("summary"):
                    f.write("## 📝 Persistent Memory Summary\n\n")
                    f.write(f"```\n{meta.get('summary')}\n```\n\n")

                f.write("## 💬 Conversation Timeline\n\n")
                for m in messages:
                    role_icon = "👤" if m.get("role") == "user" else "🤖"
                    f.write(f"### {role_icon} {m.get('role', '').upper()} `[{m.get('timestamp')}]`\n\n")
                    f.write(f"{m.get('content')}\n\n---\n\n")
            return export_file

        else: # Default TXT
            export_file = target_dir / f"{session_id}_export.txt"
            with open(export_file, "w", encoding="utf-8") as f:
                f.write(f"=== Session Export: {meta.get('title', session_id)} ({session_id}) ===\n")
                f.write(f"Created At: {meta.get('created_at')}\n")
                f.write(f"Exported At: {get_iso_timestamp()}\n")
                f.write(f"Total Messages: {len(messages)}\n")
                f.write(f"Extracted Facts: {json.dumps(meta.get('facts', {}))}\n\n")

                for m in messages:
                    role = m.get("role", "unknown").upper()
                    timestamp = m.get("timestamp", "")
                    content = m.get("content", "")
                    f.write(f"[{timestamp}] {role}:\n{content}\n\n" + "-" * 40 + "\n\n")

            return export_file
