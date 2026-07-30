import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "2000"))
MAX_REVISIONS = int(os.getenv("MAX_REVISIONS", "1"))
MAX_HISTORY_LIMIT = int(os.getenv("MAX_HISTORY_LIMIT", "100"))
CALCULATOR_MAX_NESTING = int(os.getenv("CALCULATOR_MAX_NESTING", "50"))

USE_DEMO_LLM = os.getenv("USE_DEMO_LLM", "").lower() in ("1", "true", "yes")


def get_llm():
    if USE_DEMO_LLM:
        return f"ollama/{LLM_MODEL}"
    if LLM_PROVIDER == "openai":
        return f"openai/{OPENAI_MODEL_NAME}"
    return f"ollama/{LLM_MODEL}"
