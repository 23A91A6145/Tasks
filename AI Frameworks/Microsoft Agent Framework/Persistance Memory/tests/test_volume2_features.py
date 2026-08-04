"""
Unit tests for Volume 2 Persistent Memory System features:
Session Indexing, Semantic Fact Extraction, History Search, and Storage Compaction.
"""

import pytest
from app.config import AppConfig
from app.memory import PersistentMemoryManager
from app.thread import AgentThread
from app.agent import ChatAgent

def test_semantic_fact_extraction(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)

    facts = mem.extract_facts_from_text("My name is Charlie and I am a Lead AI Engineer.")
    assert facts.get("name") == "Charlie"
    assert facts.get("role") == "Lead AI Engineer"

    tech_facts = mem.extract_facts_from_text("My tech stack is Python, Docker, and PyTest.")
    assert "Python" in tech_facts.get("tech_stack", "")

def test_session_indexing_and_titling(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)

    session_id = "test_vol2_session"
    mem.save_user_message(session_id, "My name is Alice and I live in Seattle.")

    # Check index metadata
    meta = mem.provider.get_session_meta(session_id)
    assert meta["id"] == session_id
    assert "Alice" in meta["title"] or "My name" in meta["title"]
    assert meta["facts"].get("name") == "Alice"
    assert meta["facts"].get("location") == "Seattle"

def test_history_search(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)

    s1 = "session_alpha"
    s2 = "session_beta"

    mem.save_user_message(s1, "Deploying application to Kubernetes cluster.")
    mem.save_user_message(s2, "Refactoring database query using PostgreSQL.")

    # Search for kubernetes
    k8s_results = mem.search("kubernetes")
    assert len(k8s_results) == 1
    assert k8s_results[0]["session_id"] == s1

    # Search across all
    db_results = mem.search("postgresql")
    assert len(db_results) == 1
    assert db_results[0]["session_id"] == s2

def test_storage_compaction(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    sid = "compact_test"

    mem.save_user_message(sid, "Turn 1")
    mem.save_assistant_message(sid, "Reply 1", model="mock")

    count = mem.compact(sid)
    assert count == 2

def test_system_prompt_and_fact_context_injection(tmp_path):
    history_dir = tmp_path / "history"
    logs_dir = tmp_path / "logs"
    config = AppConfig(history_dir=history_dir, logs_dir=logs_dir, llm_provider="mock")

    sid = "fact_recall_vol2"
    mem = PersistentMemoryManager(history_dir)
    thread = AgentThread(session_id=sid, memory_manager=mem)
    agent = ChatAgent(config)

    # Turn 1: Save facts
    thread.add_user_message("My name is David and my tech stack is Python and PyTorch.")
    ctx1 = thread.get_context()
    resp1 = agent.generate_response("My name is David and my tech stack is Python and PyTorch.", ctx1)
    thread.add_assistant_message(resp1, model=agent.model_name)

    # Verify facts were extracted into thread
    facts = thread.get_extracted_facts()
    assert facts.get("name") == "David"

    # Turn 2: Recall facts
    ctx2 = thread.get_context()

    # System context contains injected facts header
    system_msg = [m for m in ctx2 if m["role"] == "system"][0]
    assert "David" in system_msg["content"]

    resp2 = agent.generate_response("What do you know about me?", ctx2)
    assert "David" in resp2
