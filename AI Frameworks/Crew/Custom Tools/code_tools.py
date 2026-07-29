import json as json_mod
import subprocess
import sys

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class RunPythonInput(BaseModel):
    code: str = Field(description="Python code to execute")
    timeout: int = Field(default=10, ge=1, le=60, description="Execution timeout in seconds")


@tool(args_schema=RunPythonInput)
def run_python(code: str, timeout: int = 10) -> str:
    """Execute Python code in a subprocess and return stdout.

    Args:
        code: Python code to run.
        timeout: Max execution time.

    Returns:
        stdout of the executed code, or error message.
    """
    if "import os" in code and ("system(" in code or "popen(" in code or "subprocess" in code):
        return "Error: os.system/popen and subprocess calls are not allowed for security."

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            return f"Error (exit {result.returncode}): {err[:500]}"
        output = result.stdout.strip()
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: execution timed out after {timeout}s"
    except Exception as e:
        return f"Error executing code: {e}"


class FormatCodeInput(BaseModel):
    code: str = Field(description="Python code to format")
    line_length: int = Field(default=88, ge=40, le=120, description="Max line length")


@tool(args_schema=FormatCodeInput)
def format_code(code: str, line_length: int = 88) -> str:
    """Format Python code using ruff.

    Args:
        code: Python source code.
        line_length: Max line length.

    Returns:
        Formatted code.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--line-length", str(line_length), "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        pass

    try:
        import autopep8
        formatted = autopep8.fix_code(code, options={"max_line_length": line_length})
        return formatted
    except ImportError:
        pass

    return code


class ValidateJsonInput(BaseModel):
    value: str = Field(description="JSON string to validate")


@tool(args_schema=ValidateJsonInput)
def validate_json(value: str) -> dict:
    """Validate a JSON string and return result with details.

    Args:
        value: JSON string to validate.

    Returns:
        Dict with valid (bool), error (str|null), and parsed (object|null).
    """
    try:
        parsed = json_mod.loads(value)
        return {"valid": True, "error": None, "parsed_type": type(parsed).__name__}
    except json_mod.JSONDecodeError as e:
        return {"valid": False, "error": str(e), "parsed_type": None}
