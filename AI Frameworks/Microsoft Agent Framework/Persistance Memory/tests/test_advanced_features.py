"""
Unit tests for Advanced Upgraded Features:
System Health Check Audit, Standalone HTML Exporter, Fact Mutation (forget/setfact), Session Cloning & Deletion.
"""

import pytest
from app.config import AppConfig
from app.memory import PersistentMemoryManager
from app.health import SystemHealthCheck

def test_system_health_audit(tmp_path):
    history_dir = tmp_path / "history"
    logs_dir = tmp_path / "logs"
    config = AppConfig(history_dir=history_dir, logs_dir=logs_dir, llm_provider="mock")

    health_check = SystemHealthCheck(config)
    audit = health_check.run_health_audit()

    assert audit["status"] == "HEALTHY"
    assert isinstance(audit["free_disk_gb"], float)
    assert audit["active_provider"] == "mock"

def test_html_export(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    sid = "html_export_test"

    mem.save_user_message(sid, "My name is Grace")
    mem.save_assistant_message(sid, "Hello Grace", model="mock")

    html_file = mem.provider.export_history(sid, export_format="html")
    assert html_file is not None
    assert html_file.suffix == ".html"
    assert html_file.exists()

    content = html_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Grace" in content

def test_fact_mutation_set_and_forget(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    sid = "fact_mutation_test"

    mem.save_user_message(sid, "My name is Henry")
    assert mem.get_extracted_facts(sid).get("name") == "Henry"

    # Override fact
    mem.provider.set_fact(sid, "name", "Henry Ford")
    assert mem.get_extracted_facts(sid).get("name") == "Henry Ford"

    # Remove fact
    removed = mem.provider.remove_fact(sid, "name")
    assert removed is True
    assert "name" not in mem.get_extracted_facts(sid)

def test_session_cloning_and_deletion(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    source_sid = "source_session"
    target_sid = "cloned_session"

    mem.save_user_message(source_sid, "Clonable message 1")
    mem.save_assistant_message(source_sid, "Clonable response 1", model="mock")

    # Clone
    cloned = mem.provider.clone_session(source_sid, target_sid)
    assert cloned is True

    cloned_msgs = mem.load_session_history(target_sid)
    assert len(cloned_msgs) == 2
    assert cloned_msgs[0]["content"] == "Clonable message 1"

    # Delete target
    deleted = mem.clear_session(target_sid)
    assert deleted is True
    assert len(mem.load_session_history(target_sid)) == 0
