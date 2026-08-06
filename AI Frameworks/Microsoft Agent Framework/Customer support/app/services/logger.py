import os
import logging
from app.config import LOGS_DIR

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logger(name: str, log_file: str, level=logging.INFO, formatter=None) -> logging.Logger:
    """Sets up a logger with a file handler."""
    filepath = os.path.join(LOGS_DIR, log_file)
    handler = logging.FileHandler(filepath)
    if formatter is None:
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        logger.addHandler(handler)
    logger.propagate = False
    return logger

# Configure specific loggers
chat_formatter = logging.Formatter('%(asctime)s [%(levelname)s] - Session: %(session_id)s - %(author)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
routing_formatter = logging.Formatter('%(asctime)s - Session: %(session_id)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
error_formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

_chat_logger = setup_logger("chat_logger", "chat.log", formatter=chat_formatter)
_routing_logger = setup_logger("routing_logger", "routing.log", formatter=routing_formatter)
_error_logger = setup_logger("error_logger", "errors.log", formatter=error_formatter)

def log_chat(session_id: str, role: str, author: str, message: str):
    """Logs a chat message to chat.log."""
    _chat_logger.info(message, extra={"session_id": session_id, "author": f"{role.upper()} ({author})"})

def log_routing(session_id: str, source: str, target: str):
    """Logs an agent handoff to routing.log."""
    _routing_logger.info(f"Handoff: {source} -> {target}", extra={"session_id": session_id})

def log_error(message: str, exc_info=None):
    """Logs an error or exception to errors.log."""
    if exc_info:
        _error_logger.error(message, exc_info=exc_info)
    else:
        _error_logger.warning(message)
