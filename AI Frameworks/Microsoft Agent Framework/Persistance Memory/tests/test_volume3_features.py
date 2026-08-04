"""
Unit tests for Volume 3 Professional Features:
AnalyticsEngine, Multi-format History Exporter (TXT, MD, JSON), Role Filtering, and Response Latency Tracking.
"""

import json
import pytest
from app.config import AppConfig
from app.memory import PersistentMemoryManager
from app.thread import AgentThread
from app.agent import ChatAgent
from app.analytics import AnalyticsEngine

def test_analytics_engine(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    sid = "analytics_test_session"

    mem.save_user_message(sid, "My name is Eve and I work with PyTorch.")
    mem.save_assistant_message(sid, "Hello Eve!", model="mock")

    engine = AnalyticsEngine(mem.provider)
    s_analytics = engine.get_session_analytics(sid)

    assert s_analytics["session_id"] == sid
    assert s_analytics["total_messages"] == 2
    assert s_analytics["user_messages"] == 1
    assert s_analytics["assistant_messages"] == 1
    assert s_analytics["total_tokens"] > 0
    assert s_analytics["facts_count"] >= 1

    sys_analytics = engine.get_system_analytics()
    assert sys_analytics["total_sessions"] >= 1
    assert sys_analytics["grand_total_messages"] >= 2
    assert sys_analytics["grand_total_tokens"] > 0

def test_multiformat_export(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    sid = "export_format_test"

    mem.save_user_message(sid, "Hello AI")
    mem.save_assistant_message(sid, "Hello User", model="mock")

    # TXT export
    txt_file = mem.provider.export_history(sid, export_format="txt")
    assert txt_file is not None and txt_file.suffix == ".txt"
    assert txt_file.exists()

    # MD export
    md_file = mem.provider.export_history(sid, export_format="md")
    assert md_file is not None and md_file.suffix == ".md"
    assert md_file.exists()
    md_content = md_file.read_text(encoding="utf-8")
    assert "# 📜 Session History Export" in md_content

    # JSON export
    json_file = mem.provider.export_history(sid, export_format="json")
    assert json_file is not None and json_file.suffix == ".json"
    assert json_file.exists()
    json_data = json.loads(json_file.read_text(encoding="utf-8"))
    assert "metadata" in json_data
    assert len(json_data["messages"]) == 2

def test_role_based_history_filtering(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    sid = "filter_test"

    mem.save_user_message(sid, "User Question 1")
    mem.save_assistant_message(sid, "Assistant Answer 1", model="mock")
    mem.save_user_message(sid, "User Question 2")

    user_only = mem.provider.load_history(sid, role_filter="user")
    assert len(user_only) == 2
    assert all(m["role"] == "user" for m in user_only)

    asst_only = mem.provider.load_history(sid, role_filter="assistant")
    assert len(asst_only) == 1
    assert asst_only[0]["role"] == "assistant"

def test_response_latency_tracking(tmp_path):
    history_dir = tmp_path / "history"
    logs_dir = tmp_path / "logs"
    config = AppConfig(history_dir=history_dir, logs_dir=logs_dir, llm_provider="mock")

    agent = ChatAgent(config)
    resp, latency_ms = agent.generate_response_with_latency("Hello", [{"role": "user", "content": "Hello"}])

    assert isinstance(resp, str)
    assert len(resp) > 0
    assert isinstance(latency_ms, float)
    assert latency_ms >= 0.0
