"""Application configuration loaded from environment / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# apps/backend/ — relative DATABASE_URL / STORAGE_DIR paths resolve here so the
# server, workers and scripts all hit the same files regardless of CWD.
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "TenantDesk AI"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./dev.db"

    SECRET_KEY: str = "dev-secret-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # log = dev email (prints reset links, returns them to the UI) |
    # smtp = real delivery via the provider settings below
    EMAIL_MODE: str = "log"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "no-reply@tenantdesk.local"

    # ── Volume 2 · AI engine ────────────────────────────────────────────────
    # auto | crewai | llm | fallback
    AI_ENGINE: str = "auto"
    # openai | groq | openrouter | ollama | custom
    LLM_PROVIDER: str = "openai"
    LLM_BASE_URL: str = ""
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    # ── Volume 2 · Knowledge (RAG) ──────────────────────────────────────────
    # hash | openai | local   (hash = free, offline, no API key)
    EMBEDDINGS_PROVIDER: str = "hash"
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    EMBEDDINGS_BASE_URL: str = ""
    EMBEDDINGS_API_KEY: str = ""
    EMBEDDINGS_DIM: int = 384

    # numpy | qdrant   (numpy = free, no Docker; qdrant = via QDRANT_URL)
    VECTOR_STORE: str = "numpy"
    QDRANT_URL: str = ""

    STORAGE_DIR: str = "./storage"
    MAX_UPLOAD_MB: int = 25
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 150
    SEARCH_TOP_K: int = 5

    @field_validator("DATABASE_URL")
    @classmethod
    def _resolve_sqlite(cls, url: str) -> str:
        """Anchor relative sqlite:/// paths to apps/backend regardless of CWD."""
        prefix = "sqlite:///"
        if not url.startswith(prefix):
            return url
        raw = url[len(prefix):]
        if raw in ("", ":memory:") or raw.startswith("/"):
            return url
        return f"{prefix}{(BACKEND_DIR / raw).resolve()}"

    @field_validator("STORAGE_DIR")
    @classmethod
    def _resolve_dir(cls, path: str) -> str:
        p = Path(path)
        if p.is_absolute():
            return str(p)
        return str((BACKEND_DIR / p).resolve())


settings = Settings()
