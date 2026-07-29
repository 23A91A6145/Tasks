import json
import logging
import logging.handlers
import sys
import traceback
from contextvars import ContextVar
from datetime import datetime, timezone

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
session_id: ContextVar[str | None] = ContextVar("session_id", default=None)


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        rid = request_id.get()
        sid = session_id.get()
        if rid:
            log["request_id"] = rid
        if sid:
            log["session_id"] = sid
        if record.exc_info and record.exc_info[0]:
            log["exception"] = traceback.format_exception(*record.exc_info)
        if hasattr(record, "extra_fields"):
            log.update(record.extra_fields)
        return json.dumps(log, default=str)


def setup_logging(
    level: str = "INFO",
    json_output: bool = True,
    log_file: str | None = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    root = logging.getLogger("crew_tools")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    if json_output:
        fmt = StructuredFormatter()
    else:
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    root.addHandler(console)

    if log_file:
        rf = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        rf.setFormatter(StructuredFormatter())
        root.addHandler(rf)

    return root


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"crew_tools.{name}")


class LoggerMixin:
    @property
    def log(self) -> logging.Logger:
        if not hasattr(self, "_log"):
            self._log = get_logger(type(self).__name__)
        return self._log
