"""
Unit tests for app/config.py
"""

import pytest
from app.config import AppConfig, load_config

def test_default_config(tmp_path):
    config = AppConfig(
        history_dir=tmp_path / "history",
        logs_dir=tmp_path / "logs"
    )
    assert config.llm_provider in ("mock", "ollama", "groq", "gemini")
    assert config.history_dir.exists()
    assert config.logs_dir.exists()
    assert config.default_session_id == "session_001"

def test_load_config_helper():
    config = load_config()
    assert isinstance(config, AppConfig)
