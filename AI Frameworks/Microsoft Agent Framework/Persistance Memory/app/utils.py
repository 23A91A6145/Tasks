"""
Logging, token estimation, and formatting utilities for Persistent Memory Chat CLI.
"""

import os
import logging
from datetime import datetime
from pathlib import Path

def setup_logger(logs_dir: Path) -> logging.Logger:
    """Configures structured file logger for chat and error tracking."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("PersistentChatCLI")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    chat_handler = logging.FileHandler(logs_dir / "chat.log", encoding="utf-8")
    chat_handler.setLevel(logging.INFO)
    chat_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    chat_handler.setFormatter(chat_formatter)

    error_handler = logging.FileHandler(logs_dir / "error.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    error_handler.setFormatter(error_formatter)

    logger.addHandler(chat_handler)
    logger.addHandler(error_handler)

    return logger

def estimate_tokens(text: str) -> int:
    """Approximates word-to-token count (~4 chars per token average)."""
    if not text:
        return 0
    return max(1, len(text.strip()) // 4)

def get_iso_timestamp() -> str:
    """Returns current ISO timestamp string."""
    return datetime.now().isoformat(timespec="seconds")

def format_human_timestamp(iso_str: str) -> str:
    """Converts ISO timestamp into readable string."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_str
