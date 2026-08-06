"""
Centralized application configuration.

Phase 4.2 (Configuration): Every tunable value lives in `.env` (via dotenv)
and is loaded here once. The rest of the application imports these settings
instead of reading environment variables directly, keeping configuration
auditable, typed, and easy to override in Docker/CI.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _path(name: str, default: str) -> Path:
    raw = os.getenv(name, default)
    return Path(raw).expanduser().resolve() if not Path(raw).is_absolute() else Path(raw)


@dataclass(frozen=True)
class Settings:
    # Server
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))

    # Directories
    base_dir: Path = BASE_DIR
    log_dir: Path = field(default_factory=lambda: _path("LOG_DIR", str(BASE_DIR / "logs")))
    checkpoint_dir: Path = field(default_factory=lambda: _path("CHECKPOINT_DIR", str(BASE_DIR / "checkpoints")))
    template_dir: Path = field(default_factory=lambda: BASE_DIR / "templates")

    # Log file paths
    audit_log_path: Path = field(default_factory=lambda: _path("AUDIT_LOG_PATH", str(BASE_DIR / "logs" / "audit.log")))
    approval_log_path: Path = field(default_factory=lambda: _path("APPROVAL_LOG_PATH", str(BASE_DIR / "logs" / "approvals.log")))
    error_log_path: Path = field(default_factory=lambda: _path("ERROR_LOG_PATH", str(BASE_DIR / "logs" / "errors.log")))

    # LLM provider: mock | groq | ollama
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    ollama_api_base: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "llama3-8b-8192")

    # Policy / HITL thresholds (USD)
    max_auto_approve_amount: float = float(os.getenv("MAX_AUTO_APPROVE_AMOUNT", "0.0"))
    manager_limit: float = float(os.getenv("MANAGER_LIMIT", "100.0"))
    max_refund_ceiling: float = float(os.getenv("MAX_REFUND_CEILING", "1000000.0"))

    # SLA: seconds a request may remain pending before auto-expiring
    approval_sla_timeout_seconds: int = int(os.getenv("APPROVAL_SLA_TIMEOUT_SECONDS", "300"))

    # Security
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
    session_id_header: str = os.getenv("SESSION_ID_HEADER", "x-session-id")
    reviewer_override_header: str = os.getenv("REVIEWER_OVERRIDE_HEADER", "x-reviewer-override")

    # Demo / seeding
    seed_demo_data: bool = os.getenv("SEED_DEMO_DATA", "true").lower() in ("1", "true", "yes")

    def ensure_dirs(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
