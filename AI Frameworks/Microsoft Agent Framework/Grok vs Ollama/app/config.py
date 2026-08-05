import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

class Config:
    # API Keys & URLs
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_DEFAULT_MODEL = os.getenv("GROQ_DEFAULT_MODEL", "llama-3.3-70b-versatile").strip()
    
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
    OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2:1b").strip()
    
    # Benchmarking Defaults
    BENCHMARK_TIMEOUT = int(os.getenv("BENCHMARK_TIMEOUT", "60"))
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.2"))
    DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1024"))
    
    # Logging & Paths
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip()
    LOG_DIR = BASE_DIR / "logs"
    RESULTS_DIR = BASE_DIR / "results"
    CHARTS_DIR = RESULTS_DIR / "charts"
    REPORTS_DIR = RESULTS_DIR / "reports"
    DATASETS_DIR = BASE_DIR / "datasets"

    @classmethod
    def create_dirs(cls):
        """Ensure all required directories exist."""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# Instantiate directories
Config.create_dirs()
