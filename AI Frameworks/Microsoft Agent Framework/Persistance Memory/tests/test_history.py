"""
Unit tests for app/history.py (FileHistoryProvider)
"""

import pytest
from app.history import FileHistoryProvider

def test_file_history_provider_crud(tmp_path):
    provider = FileHistoryProvider(tmp_path)
    session_id = "test_session_01"

    # Initially empty
    messages = provider.load_history(session_id)
    assert len(messages) == 0

    # Append user message
    msg1 = provider.append_message(session_id, role="user", content="My name is Bob")
    assert msg1["role"] == "user"
    assert msg1["content"] == "My name is Bob"

    # Append assistant message
    msg2 = provider.append_message(session_id, role="assistant", content="Hello Bob", model="mock")
    assert msg2["role"] == "assistant"

    # Load history
    loaded = provider.load_history(session_id)
    assert len(loaded) == 2
    assert loaded[0]["content"] == "My name is Bob"
    assert loaded[1]["content"] == "Hello Bob"

    # Check stats
    stats = provider.get_session_stats(session_id)
    assert stats["total_messages"] == 2
    assert stats["user_messages"] == 1
    assert stats["assistant_messages"] == 1
    assert stats["total_tokens"] > 0

    # List sessions
    sessions = provider.list_sessions()
    session_ids = [s["id"] for s in sessions]
    assert session_id in session_ids

    # Export history
    export_file = provider.export_history(session_id)
    assert export_file is not None
    assert export_file.exists()

    # Clear history
    cleared = provider.clear_history(session_id)
    assert cleared is True
    assert len(provider.load_history(session_id)) == 0
