"""
Unit tests for app/thread.py and app/agent.py demonstrating Persistent Memory Recall across restarts.
"""

import pytest
from app.config import AppConfig
from app.memory import PersistentMemoryManager
from app.thread import AgentThread
from app.agent import ChatAgent

def test_persistent_memory_recall_across_restarts(tmp_path):
    history_dir = tmp_path / "history"
    logs_dir = tmp_path / "logs"
    config = AppConfig(history_dir=history_dir, logs_dir=logs_dir, llm_provider="mock")
    
    session_id = "persistent_test_01"

    # --- RUN 1 ---
    memory_manager1 = PersistentMemoryManager(history_dir)
    thread1 = AgentThread(session_id=session_id, memory_manager=memory_manager1)
    agent1 = ChatAgent(config)

    # User tells AI their name
    thread1.add_user_message("My name is Alice")
    context1 = thread1.get_context()
    resp1 = agent1.generate_response("My name is Alice", context1)
    thread1.add_assistant_message(resp1, model=agent1.model_name)

    assert len(thread1.messages) == 2

    # --- RUN 2 (App Restarted: simulate fresh objects loading from same disk path) ---
    memory_manager2 = PersistentMemoryManager(history_dir)
    thread2 = AgentThread(session_id=session_id, memory_manager=memory_manager2)
    agent2 = ChatAgent(config)

    # Verify past messages are restored from disk
    assert len(thread2.messages) == 2
    assert thread2.messages[0]["content"] == "My name is Alice"

    # User asks "Who am I?"
    thread2.add_user_message("Who am I?")
    context2 = thread2.get_context()
    resp2 = agent2.generate_response("Who am I?", context2)

    # Verify AI recalls Alice from persistent JSONL storage!
    assert "Alice" in resp2
