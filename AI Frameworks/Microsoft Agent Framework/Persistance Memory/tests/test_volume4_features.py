"""
Unit tests for Volume 4 Production Features:
Memory Compactor, Sliding Window Summarization, Provider Fallback Circuit Breaker, and Error Recovery.
"""

import json
import pytest
from app.config import AppConfig
from app.memory import PersistentMemoryManager
from app.thread import AgentThread
from app.agent import ChatAgent
from app.compaction import MemoryCompactor

def test_memory_compactor_sliding_window(tmp_path):
    messages = [
        {"role": "user", "content": f"User turn {i}"} if i % 2 == 1 else {"role": "assistant", "content": f"Assistant turn {i}"}
        for i in range(1, 11)
    ]

    # Max context set to 4
    recent, summary = MemoryCompactor.process_sliding_window(messages, max_context=4)

    assert len(recent) == 4
    assert recent[0]["content"] == "User turn 7"
    assert recent[-1]["content"] == "Assistant turn 10"
    assert "Past Conversation Summary:" in summary
    assert "User turn 1" in summary

def test_persistent_memory_summary_in_thread_context(tmp_path):
    history_dir = tmp_path / "history"
    logs_dir = tmp_path / "logs"
    config = AppConfig(history_dir=history_dir, logs_dir=logs_dir, llm_provider="mock", max_context_messages=4)

    mem = PersistentMemoryManager(history_dir)
    thread = AgentThread(session_id="compaction_test", memory_manager=mem, max_context=4)

    # Add 8 turns
    for i in range(1, 9):
        thread.add_user_message(f"Message number {i}")
        thread.add_assistant_message(f"Response number {i}", model="mock")

    ctx = thread.get_context()
    sys_msg = [m for m in ctx if m["role"] == "system"][0]

    # Verify summary section is present in system prompt
    assert "[Persistent Memory Summary" in sys_msg["content"]

def test_provider_fallback_circuit_breaker(tmp_path):
    history_dir = tmp_path / "history"
    logs_dir = tmp_path / "logs"

    # Set provider to ollama pointing to bad URL to force network error
    config = AppConfig(
        history_dir=history_dir,
        logs_dir=logs_dir,
        llm_provider="ollama",
        ollama_base_url="http://localhost:99999"
    )

    agent = ChatAgent(config)
    ctx = [{"role": "user", "content": "Hello AI"}]

    # Generate response - should NOT crash, circuit breaker catches error & routes to Mock!
    resp, latency_ms = agent.generate_response_with_latency("Hello AI", ctx)

    assert agent.fallback_active is True
    assert "[Fallback Circuit Breaker Active]" in resp
    assert "Local Mock Engine" in resp

def test_corrupted_jsonl_recovery(tmp_path):
    history_dir = tmp_path / "history"
    mem = PersistentMemoryManager(history_dir)
    sid = "corrupt_test"

    # Write good line, corrupt line, and good line
    sess_file = history_dir / f"{sid}.jsonl"
    with open(sess_file, "w", encoding="utf-8") as f:
        f.write('{"role": "user", "content": "Valid line 1"}\n')
        f.write('CORRUPTED NON JSON LINE HERE\n')
        f.write('{"role": "assistant", "content": "Valid line 2"}\n')

    # Load history - should recover valid lines and skip corrupted line
    msgs = mem.load_session_history(sid)
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Valid line 1"
    assert msgs[1]["content"] == "Valid line 2"

    # Compact should fix the file on disk
    retained = mem.compact(sid)
    assert retained == 2
