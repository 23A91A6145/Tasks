import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "tickets.db"))

# LLM Configuration
# Default to local ollama with qwen2.5-coder:7b as primary, and llama3.2:3b as fallback
DEFAULT_MODEL = "ollama:qwen2.5-coder:7b"
LLM_MODEL = os.getenv("LLM_MODEL", DEFAULT_MODEL)
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "ollama:llama3.2:3b")

# Ollama API configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# API Keys (optional, for Groq or Google Gemini cloud)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# App environment
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

# Ensure required environment variables are set for Pydantic AI if using third-party APIs
models_to_check = [LLM_MODEL.lower(), FALLBACK_MODEL.lower()]

for m in models_to_check:
    if "groq" in m and GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    if "google" in m and GOOGLE_API_KEY:
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    if "ollama" in m:
        os.environ["OLLAMA_BASE_URL"] = OLLAMA_BASE_URL
