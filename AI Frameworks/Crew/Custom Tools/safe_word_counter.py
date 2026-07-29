from typing import Any

from langchain_core.tools import tool

from crew_tools.validation import validate_non_empty


@tool
def word_counter_safe(text: Any = "") -> str:
    """Count words with input validation.

    Returns 0 for empty text.
    Handles None, non-string, and whitespace-only input gracefully.

    Args:
        text: The text to count words in.

    Returns:
        Word count as string (or error message).
    """
    if text is None:
        return "Error: text cannot be None"
    if not isinstance(text, str):
        return f"Error: text must be a string, got {type(text).__name__}"
    if not text.strip():
        return "0"
    return str(len(text.split()))


@tool
def word_counter_advanced(
    text: str,
    ignore_numbers: bool = False,
    min_word_length: int = 1,
) -> str:
    """Count words with validation + safe error handling.

    Validates all inputs before processing.
    Returns structured error messages instead of crashing.

    Args:
        text: The text to analyze.
        ignore_numbers: Skip numeric tokens.
        min_word_length: Min chars per token (clamped to 1-100).

    Returns:
        Word count string or error description.
    """
    try:
        validate_non_empty(text, "text")
    except ValueError as e:
        return f"Error: {e}"

    if not isinstance(min_word_length, int):
        return f"Error: min_word_length must be an integer, got {type(min_word_length).__name__}"
    min_word_length = max(1, min(100, min_word_length))

    tokens = text.split()
    if ignore_numbers:
        tokens = [t for t in tokens if not t.isdigit()]
    tokens = [t for t in tokens if len(t) >= min_word_length]
    return str(len(tokens))
