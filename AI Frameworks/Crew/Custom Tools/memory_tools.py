import json
import threading
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field

_session_store: dict[str, Any] = {}
_session_lock = threading.Lock()


class SessionSetInput(BaseModel):
    key: str = Field(description="Session key")
    value: Any = Field(description="Value to store")


@tool(args_schema=SessionSetInput)
def session_set(key: str, value: Any) -> str:
    """Store a value in the session memory.

    Args:
        key: Session key.
        value: Value to store (JSON-serializable).

    Returns:
        Confirmation message.
    """
    with _session_lock:
        _session_store[key] = value
    return f"Stored key '{key}'"


class SessionGetInput(BaseModel):
    key: str = Field(description="Session key to retrieve")


@tool(args_schema=SessionGetInput)
def session_get(key: str) -> str:
    """Retrieve a value from session memory.

    Args:
        key: Session key.

    Returns:
        Stored value as JSON, or error.
    """
    with _session_lock:
        value = _session_store.get(key)
    if value is None:
        return f"Key '{key}' not found in session"
    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


@tool
def session_list() -> str:
    """List all keys in session memory.

    Returns:
        JSON list of keys.
    """
    with _session_lock:
        keys = list(_session_store.keys())
    if not keys:
        return "Session is empty."
    return json.dumps(keys, indent=2)


@tool
def session_clear() -> str:
    """Clear all values from session memory.

    Returns:
        Confirmation message.
    """
    with _session_lock:
        count = len(_session_store)
        _session_store.clear()
    return f"Cleared {count} keys from session"
