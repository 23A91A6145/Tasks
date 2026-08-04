"""
Unit tests for Volume 5 Deployment & Portfolio Features:
Verifies Docker configuration files, end-to-end demo execution, and portfolio artifacts.
"""

import os
from pathlib import Path
import pytest
from app.config import load_config
from demo import run_demo

def test_docker_configuration_files():
    base_dir = Path(__file__).parent.parent
    dockerfile = base_dir / "Dockerfile"
    docker_compose = base_dir / "docker-compose.yml"

    assert dockerfile.exists()
    assert docker_compose.exists()

    df_content = dockerfile.read_text()
    dc_content = docker_compose.read_text()

    assert "FROM python:" in df_content
    assert "CMD [\"python\", \"main.py\"]" in df_content
    assert "persistent-chat-cli" in dc_content or "persistent_chat_cli" in dc_content

def test_end_to_end_demo_run():
    # Execute full end-to-end demo script
    try:
        run_demo()
        success = True
    except Exception as e:
        success = False

    assert success is True

def test_exported_artifacts_exist():
    base_dir = Path(__file__).parent.parent
    history_dir = base_dir / "history"

    md_export = history_dir / "demo_portfolio_session_export.md"
    json_export = history_dir / "demo_portfolio_session_export.json"

    assert md_export.exists()
    assert json_export.exists()
