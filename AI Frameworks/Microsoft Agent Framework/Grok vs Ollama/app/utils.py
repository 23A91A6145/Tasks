import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from app.config import Config

# Custom theme for styling console output
console_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "bold green",
    "header": "bold white on blue",
    "metric_label": "bold yellow",
    "metric_val": "bold white"
})

console = Console(theme=console_theme)

def setup_logging():
    """Sets up dual file logging and a rich console logger."""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # Root logger configuration
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture everything, filter in handlers
    
    # Remove existing handlers if any
    logger.handlers.clear()
    
    # Formatter for file logging
    file_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 1. Info File Handler (all messages >= INFO)
    info_handler = logging.FileHandler(Config.LOG_DIR / "benchmark.log")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_formatter)
    logger.addHandler(info_handler)
    
    # 2. Error File Handler (only ERROR messages)
    error_handler = logging.FileHandler(Config.LOG_DIR / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # 3. Rich Console Handler
    console_handler = RichHandler(
        console=console,
        show_time=True,
        omit_repeated_times=False,
        level=log_level
    )
    logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Gets a logger for a specific module."""
    return logging.getLogger(name)

def get_ram_usage() -> float:
    """Returns the current system RAM usage in GB by reading /proc/meminfo (Linux)."""
    try:
        total = 0.0
        available = 0.0
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total = float(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    available = float(line.split()[1])
        used = total - available
        return round(used / 1024 / 1024, 2)
    except Exception:
        # Fallback to 0.0 if not Linux or file not found
        return 0.0

# Auto setup logging on import
setup_logging()
logger = get_logger("utils")
