import os
import json
import sqlite3
import logging
import contextlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from configs.settings import PROJECT_ROOT

logger = logging.getLogger("DatabaseManager")
DB_PATH = PROJECT_ROOT / "logs" / "skills_provider.db"

class DatabaseManager:
    """
    Manages SQLite database operations for persisting execution history,
    skill metrics, and custom runtime priority overrides.
    """
    
    def __init__(self):
        self.db_path = DB_PATH
        # Ensure parent directory exists
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes tables for execution logs, performance metrics, and overrides."""
        logger.info(f"Initializing database at {self.db_path}")
        with contextlib.closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            
            # 1. Execution History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    arguments TEXT NOT NULL,
                    result TEXT,
                    status TEXT NOT NULL,
                    error TEXT,
                    duration_ms REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Priority Overrides Table (dynamically editable via UI dashboard)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS priority_overrides (
                    skill_name TEXT PRIMARY KEY,
                    preferred_source TEXT NOT NULL,
                    reason TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexing for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exec_skill ON execution_history(skill_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exec_status ON execution_history(status)")
            conn.commit()

    # --- Execution History Methods ---

    def log_execution(
        self, 
        skill_name: str, 
        source_type: str, 
        source_path: str, 
        arguments: Dict[str, Any], 
        result: Optional[str], 
        status: str, 
        error: Optional[str], 
        duration_ms: float
    ):
        """Records an execution event and updates execution performance counters."""
        query = """
            INSERT INTO execution_history 
            (skill_name, source_type, source_path, arguments, result, status, error, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with contextlib.closing(self._get_connection()) as conn:
                conn.execute(query, (
                    skill_name,
                    source_type,
                    source_path,
                    json.dumps(arguments),
                    result,
                    status,
                    error,
                    duration_ms
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to write execution log to database: {e}", exc_info=True)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent execution history records."""
        query = """
            SELECT id, skill_name, source_type, source_path, arguments, result, status, error, duration_ms, created_at
            FROM execution_history
            ORDER BY id DESC
            LIMIT ?
        """
        try:
            with contextlib.closing(self._get_connection()) as conn:
                rows = conn.execute(query, (limit,)).fetchall()
                results = []
                for r in rows:
                    item = dict(r)
                    # Safe deserialize of arguments
                    try:
                        item["arguments"] = json.loads(item["arguments"])
                    except Exception:
                        item["arguments"] = {}
                    results.append(item)
                return results
        except Exception as e:
            logger.error(f"Failed to fetch execution history: {e}", exc_info=True)
            return []

    # --- Performance Metrics Methods ---

    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Aggregates execution metrics (total calls, average latency, success rates)
        grouped by skill name directly from the execution logs.
        """
        query = """
            SELECT 
                skill_name,
                COUNT(*) as total_calls,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_calls,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_calls,
                ROUND(AVG(duration_ms), 2) as avg_duration_ms
            FROM execution_history
            GROUP BY skill_name
        """
        try:
            with contextlib.closing(self._get_connection()) as conn:
                rows = conn.execute(query).fetchall()
                metrics = {}
                for r in rows:
                    row_dict = dict(r)
                    # Calculate success percentage
                    total = row_dict["total_calls"]
                    success = row_dict["success_calls"]
                    row_dict["success_rate"] = round((success / total) * 100.0, 1) if total > 0 else 0.0
                    metrics[row_dict["skill_name"]] = row_dict
                return metrics
        except Exception as e:
            logger.error(f"Failed to compile performance metrics: {e}", exc_info=True)
            return {}

    # --- Override Management Methods ---

    def save_override(self, skill_name: str, preferred_source: str, reason: Optional[str] = None):
        """Saves or updates a custom priority override for a skill."""
        query = """
            INSERT INTO priority_overrides (skill_name, preferred_source, reason, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(skill_name) DO UPDATE SET
                preferred_source = excluded.preferred_source,
                reason = excluded.reason,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            with contextlib.closing(self._get_connection()) as conn:
                conn.execute(query, (skill_name, preferred_source, reason))
                conn.commit()
                logger.info(f"Database override saved: {skill_name} -> {preferred_source} ({reason})")
        except Exception as e:
            logger.error(f"Failed to save override: {e}", exc_info=True)

    def delete_override(self, skill_name: str):
        """Removes a custom priority override from the database."""
        query = "DELETE FROM priority_overrides WHERE skill_name = ?"
        try:
            with contextlib.closing(self._get_connection()) as conn:
                conn.execute(query, (skill_name,))
                conn.commit()
                logger.info(f"Database override deleted: {skill_name}")
        except Exception as e:
            logger.error(f"Failed to delete override: {e}", exc_info=True)

    def get_overrides(self) -> Dict[str, Dict[str, Any]]:
        """Returns all database overrides as a dictionary."""
        query = "SELECT skill_name, preferred_source, reason FROM priority_overrides"
        try:
            with contextlib.closing(self._get_connection()) as conn:
                rows = conn.execute(query).fetchall()
                return {r["skill_name"]: {"preferred_source": r["preferred_source"], "reason": r["reason"]} for r in rows}
        except Exception as e:
            logger.error(f"Failed to load DB overrides: {e}", exc_info=True)
            return {}
