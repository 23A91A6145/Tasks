# Shared utilities for skill implementations
def format_skill_output(status: str, result: any, error: str = None) -> dict:
    """Standardizes return payloads for custom user skills."""
    return {
        "status": status,
        "result": result,
        "error": error
    }
