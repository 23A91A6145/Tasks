"""
Hashira ATS - Configuration & Environment Setup
Loads environment variables for Telegram Bot, Groq API, and application settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file from workspace, or fallback to /home/cherry/hashira/.env
env_paths = [
    BASE_DIR / ".env",
    Path("/home/cherry/hashira/.env"),
    Path.home() / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(dotenv_path=p, override=True)
        break

# API Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# AI Models
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))

# Bot Metadata
BOT_NAME = "Hashira ATS"
BOT_VERSION = "2.0.0"
