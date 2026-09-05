import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "ResearchOS"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/researchos"
    DATABASE_FALLBACK_SQLITE: str = "sqlite+aiosqlite:///./data/researchos.db"
    USE_SQLITE_FALLBACK: bool = True
    
    # Free Retrieval APIs
    OPENALEX_EMAIL: str = "researchos@example.com"
    ARXIV_ENABLED: bool = True
    SEMANTIC_SCHOLAR_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    BRAVE_SEARCH_API_KEY: str = ""
    
    # LLM Providers (Local / Free Tier)
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    
    # Research Execution Limits
    MAX_STEPS: int = 25
    MAX_SEARCHES: int = 12
    MAX_SOURCES: int = 30
    MAX_RUNTIME_SECONDS: int = 300
    CONFIDENCE_THRESHOLD: float = 0.75

settings = Settings()
