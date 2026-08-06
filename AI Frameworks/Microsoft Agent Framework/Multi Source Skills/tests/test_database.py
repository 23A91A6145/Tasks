import pytest
import sqlite3
import contextlib
from pathlib import Path
from agents.db_manager import DatabaseManager

@pytest.fixture
def test_db(tmp_path):
    """Fixture to initialize DatabaseManager with a temporary database path."""
    db_file = tmp_path / "test_skills.db"
    
    # Patch the DB_PATH global in db_manager temporarily
    import agents.db_manager
    original_path = agents.db_manager.DB_PATH
    agents.db_manager.DB_PATH = db_file
    
    db_mgr = DatabaseManager()
    
    yield db_mgr
    
    # Restore original path
    agents.db_manager.DB_PATH = original_path


def test_db_initialization(test_db):
    assert test_db.db_path.exists()
    
    # Verify tables exist
    with contextlib.closing(sqlite3.connect(str(test_db.db_path))) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "execution_history" in tables
        assert "priority_overrides" in tables


def test_log_and_get_history(test_db):
    # Log 1: Success execution
    test_db.log_execution(
        skill_name="test_math",
        source_type="inline",
        source_path="local:func",
        arguments={"x": 5, "y": 10},
        result="15",
        status="success",
        error=None,
        duration_ms=4.5
    )
    
    # Log 2: Failed execution
    test_db.log_execution(
        skill_name="test_math",
        source_type="inline",
        source_path="local:func",
        arguments={"x": 5, "y": 0},
        result=None,
        status="failed",
        error="ZeroDivisionError",
        duration_ms=1.2
    )

    history = test_db.get_history()
    assert len(history) == 2
    
    # Deserialized check
    latest = history[0]
    assert latest["skill_name"] == "test_math"
    assert latest["status"] == "failed"
    assert latest["error"] == "ZeroDivisionError"
    assert latest["arguments"] == {"x": 5, "y": 0}
    
    older = history[1]
    assert older["status"] == "success"
    assert older["result"] == "15"
    assert older["duration_ms"] == 4.5


def test_metrics_compilation(test_db):
    # Log successful execution
    test_db.log_execution("skill_a", "inline", "local", {}, "ok", "success", None, 10.0)
    test_db.log_execution("skill_a", "inline", "local", {}, "ok", "success", None, 20.0)
    # Log failed execution
    test_db.log_execution("skill_a", "inline", "local", {}, None, "failed", "err", 30.0)
    
    metrics = test_db.get_metrics()
    assert "skill_a" in metrics
    
    stats = metrics["skill_a"]
    assert stats["total_calls"] == 3
    assert stats["success_calls"] == 2
    assert stats["failed_calls"] == 1
    assert stats["success_rate"] == 66.7
    assert stats["avg_duration_ms"] == 20.0


def test_priority_overrides(test_db):
    # Initial overrides list should be empty
    overrides = test_db.get_overrides()
    assert len(overrides) == 0
    
    # Save override
    test_db.save_override("search", "class", "Prefer structured database query")
    overrides = test_db.get_overrides()
    assert "search" in overrides
    assert overrides["search"]["preferred_source"] == "class"
    assert overrides["search"]["reason"] == "Prefer structured database query"
    
    # Update override
    test_db.save_override("search", "file", "Override change")
    overrides = test_db.get_overrides()
    assert overrides["search"]["preferred_source"] == "file"
    
    # Delete override
    test_db.delete_override("search")
    overrides = test_db.get_overrides()
    assert "search" not in overrides
