"""
Configuration Manager for Persistent Memory Chat CLI.
Loads settings from environment variables or .env file cleanly.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

@dataclass
class AppConfig:
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").lower()
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    history_dir: Path = Path(os.getenv("HISTORY_DIR", "history"))
    logs_dir: Path = Path(os.getenv("LOGS_DIR", "logs"))
    default_session_id: str = os.getenv("DEFAULT_SESSION_ID", "session_001")
    max_context_messages: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
    
    color_theme: str = os.getenv("COLOR_THEME", "cyan")
    enable_spinner: bool = os.getenv("ENABLE_SPINNER", "true").lower() == "true"

    def __post_init__(self):
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

def load_config() -> AppConfig:
    """Helper to instantiate and return application configuration."""
    return AppConfig()
