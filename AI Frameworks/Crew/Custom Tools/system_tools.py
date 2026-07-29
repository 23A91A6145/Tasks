import os
import platform
import shutil
import sys

from langchain_core.tools import tool
from pydantic import BaseModel, Field


@tool
def system_info() -> str:
    """Get system information: OS, CPU count, memory, Python version.

    Returns:
        Formatted system information.
    """
    try:
        import psutil
        has_psutil = True
    except ImportError:
        has_psutil = False

    lines = [
        f"Platform: {platform.platform()}",
        f"Python: {sys.version}",
        f"Hostname: {platform.node()}",
        f"Architecture: {platform.machine()}",
    ]

    if has_psutil:
        lines.append(f"CPU Cores: {psutil.cpu_count(logical=True)}")
        lines.append(f"CPU Usage: {psutil.cpu_percent(interval=0)}%")
        mem = psutil.virtual_memory()
        lines.append(f"Memory: {mem.total // (1024**3)}GB total, {mem.available // (1024**3)}GB available")
        disk = psutil.disk_usage("/")
        lines.append(f"Disk: {disk.total // (1024**3)}GB total, {disk.free // (1024**3)}GB free")
    else:
        lines.append(f"CPU Cores: {os.cpu_count() or 'unknown'}")

    lines.append(f"CWD: {os.getcwd()}")
    return "\n".join(lines)


class WhichProgramInput(BaseModel):
    program: str = Field(description="Program name to locate")


@tool(args_schema=WhichProgramInput)
def which_program(program: str) -> str:
    """Locate a program on the system PATH.

    Args:
        program: Executable name.

    Returns:
        Full path or error message.
    """
    path = shutil.which(program)
    if path:
        return path
    return f"Error: '{program}' not found on PATH"


class EnvGetInput(BaseModel):
    key: str = Field(description="Environment variable name")
    default: str | None = Field(default=None, description="Default if not set")


@tool(args_schema=EnvGetInput)
def env_get(key: str, default: str | None = None) -> str:
    """Get the value of an environment variable.

    Args:
        key: Environment variable name.
        default: Fallback value if not set.

    Returns:
        Variable value or default/error.
    """
    value = os.environ.get(key)
    if value is not None:
        return value
    if default is not None:
        return default
    return f"Error: environment variable '{key}' is not set"


@tool
def os_info() -> str:
    """Get operating system details.

    Returns:
        OS name, version, and release info.
    """
    return (
        f"System: {platform.system()}\n"
        f"Release: {platform.release()}\n"
        f"Version: {platform.version()}\n"
        f"Machine: {platform.machine()}\n"
        f"Processor: {platform.processor()}"
    )
