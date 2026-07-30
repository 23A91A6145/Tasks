import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "logs" / "history.db"


class HistoryStore:
    def __init__(self, db_path: str | None = None):
        self._db_path = str(db_path) if db_path else str(DB_PATH)
        path = Path(self._db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._write_lock = threading.Lock()
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                classification TEXT NOT NULL,
                tools_used TEXT DEFAULT '[]',
                routing_rationale TEXT DEFAULT '',
                response TEXT NOT NULL,
                validated INTEGER DEFAULT 0,
                validation_report TEXT DEFAULT '',
                execution_time REAL DEFAULT 0.0
            )
        """)
        self._migrate()
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversation
            ON history(conversation_id)
        """)
        self.conn.commit()

    def _migrate(self):
        existing = {
            row[1]
            for row in self.conn.execute("PRAGMA table_info(history)").fetchall()
        }
        migrations = [
            ("conversation_id", "TEXT NOT NULL DEFAULT ''"),
            ("feedback", "INTEGER DEFAULT NULL"),
        ]
        for col_name, col_type in migrations:
            if col_name not in existing:
                self.conn.execute(
                    f"ALTER TABLE history ADD COLUMN {col_name} {col_type}"
                )

    def _dict_from_row(self, r):
        return {
            "id": r["id"],
            "conversation_id": r["conversation_id"],
            "timestamp": r["timestamp"],
            "query": r["query"],
            "classification": r["classification"],
            "tools_used": json.loads(r["tools_used"]) if r["tools_used"] else [],
            "routing_rationale": r["routing_rationale"],
            "response": r["response"],
            "validated": bool(r["validated"]),
            "validation_report": r["validation_report"],
            "execution_time": r["execution_time"],
            "feedback": r["feedback"],
        }

    def add_entry(self, query: str, classification: str, tools_used: list,
                  routing_rationale: str, response: str, validated: bool,
                  validation_report: str, execution_time: float,
                  conversation_id: str = "") -> int:
        with self._write_lock:
            self.conn.execute(
                """INSERT INTO history
                   (conversation_id, timestamp, query, classification, tools_used,
                    routing_rationale, response, validated, validation_report, execution_time)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    conversation_id,
                    datetime.now().isoformat(),
                    query,
                    classification,
                    json.dumps(list(tools_used)) if tools_used else "[]",
                    routing_rationale[:200] if routing_rationale else "",
                    response,
                    1 if validated else 0,
                    validation_report[:500] if validation_report else "",
                    round(execution_time, 2),
                ),
            )
            self.conn.commit()
            cursor = self.conn.execute("SELECT last_insert_rowid()")
            return cursor.fetchone()[0]

    def get_all(self, limit: int = 50, offset: int = 0,
                classification: str = "", search: str = "",
                conversation_id: str = ""):
        conditions = []
        params = []
        if classification:
            conditions.append("classification = ?")
            params.append(classification)
        if search:
            conditions.append("(query LIKE ? OR response LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if conversation_id:
            conditions.append("conversation_id = ?")
            params.append(conversation_id)
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        limit = min(limit, 500)
        clause = f"SELECT * FROM history {where} ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self._write_lock:
            cursor = self.conn.execute(clause, params)
            rows = cursor.fetchall()
        return [self._dict_from_row(r) for r in rows]

    def count(self, classification: str = "", search: str = "",
              conversation_id: str = ""):
        conditions = []
        params = []
        if classification:
            conditions.append("classification = ?")
            params.append(classification)
        if search:
            conditions.append("(query LIKE ? OR response LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if conversation_id:
            conditions.append("conversation_id = ?")
            params.append(conversation_id)
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        with self._write_lock:
            cursor = self.conn.execute(
                f"SELECT COUNT(*) FROM history {where}", params
            )
            return cursor.fetchone()[0]

    def get_by_id(self, entry_id: int):
        with self._write_lock:
            cursor = self.conn.execute(
                "SELECT * FROM history WHERE id = ?", (entry_id,)
            )
            r = cursor.fetchone()
        if not r:
            return None
        return self._dict_from_row(r)

    def get_conversation(self, conversation_id: str, limit: int = 200):
        return self.get_all(conversation_id=conversation_id, limit=limit)

    def update_feedback(self, entry_id: int, feedback: int):
        if feedback not in (-1, 1):
            return False
        with self._write_lock:
            self.conn.execute(
                "UPDATE history SET feedback = ? WHERE id = ?",
                (feedback, entry_id),
            )
            self.conn.commit()
            return self.conn.total_changes > 0

    def delete_entry(self, entry_id: int):
        with self._write_lock:
            self.conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
            self.conn.commit()

    def clear(self):
        with self._write_lock:
            self.conn.execute("DELETE FROM history")
            self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
