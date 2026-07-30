import os
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError
from dotenv import load_dotenv

load_dotenv()


def _check_ollama(url: str) -> bool:
    try:
        req = Request(f"{url}/api/tags", method="GET", headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except (URLError, OSError):
        return False


def _detect_provider() -> str:
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    if _check_ollama(ollama_url):
        return "ollama"
    if os.getenv("OPENAI_API_KEY", "").startswith("sk-"):
        return "openai"
    return "none"


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Crew Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "5.0.0")
    DEBUG: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    OPENAI_MODEL_TEMPERATURE: float = float(os.getenv("OPENAI_MODEL_TEMPERATURE", "0.7"))

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "llama3.2:3b")

    CREW_VERBOSE: bool = os.getenv("CREW_VERBOSE", "false").lower() == "true"
    CREW_MAX_RPM: int = int(os.getenv("CREW_MAX_RPM", "10"))
    CREW_TIMEOUT: int = int(os.getenv("CREW_TIMEOUT", "120"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/crew.log")

    MAX_QUERY_LENGTH: int = int(os.getenv("MAX_QUERY_LENGTH", "10000"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def __post_init__(self) -> None:
        if self.LOG_LEVEL not in self.VALID_LOG_LEVELS:
            self.LOG_LEVEL = "INFO"
        if not 0 < self.OPENAI_MODEL_TEMPERATURE <= 2.0:
            self.OPENAI_MODEL_TEMPERATURE = 0.7
        if self.CREW_MAX_RPM < 1:
            self.CREW_MAX_RPM = 10
        if self.CREW_TIMEOUT < 10:
            self.CREW_TIMEOUT = 120
        if self.MAX_QUERY_LENGTH < 1:
            self.MAX_QUERY_LENGTH = 10000

    @property
    def provider(self) -> str:
        return _detect_provider()

    @property
    def active_model(self) -> str:
        if self.provider == "ollama":
            return self.OLLAMA_MODEL_NAME
        return self.OPENAI_MODEL_NAME

    @property
    def is_ready(self) -> bool:
        return self.provider != "none"

    @property
    def missing_keys(self) -> list[str]:
        missing = []
        if self.provider == "none":
            missing.append("Ollama (install: curl -fsSL https://ollama.ai/install.sh | sh)")
            missing.append("OR OPENAI_API_KEY (copy .env.example to .env)")
        return missing

    def validate_or_exit(self) -> None:
        missing = self.missing_keys
        if missing:
            print(f"[{self.APP_NAME}] No LLM provider detected.")
            print("Options:")
            for item in missing:
                print(f"  - {item}")
            print("\nOllama is recommended — it's free, local, and requires no API key.")
            sys.exit(1)

    def __repr__(self) -> str:
        return (
            f"Settings("
            f"provider={self.provider}, "
            f"model={self.active_model}, "
            f"verbose={self.CREW_VERBOSE}, "
            f"log={self.LOG_LEVEL})"
        )


settings = Settings()
settings.__post_init__()
