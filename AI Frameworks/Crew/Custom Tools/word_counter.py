from langchain_core.tools import tool
from pydantic import BaseModel, Field


@tool
def word_counter_v1(text: str) -> int:
    """Count words."""
    return len(text.split())


@tool
def word_counter_v2(text: str) -> int:
    """Count the number of words in the provided text.

    Args:
        text: Input string to count words from.

    Returns:
        Total word count.
    """
    return len(text.split())


@tool
def word_counter_v3(text: str) -> int:
    """Count the number of words in the given text.

    Use this tool when the user asks for:
    - Word count or total words
    - Essay, blog, or report length
    - Writing statistics or text metrics
    - Document analysis or content measurement
    - Text size or length estimation

    Handles multiple consecutive spaces correctly.
    Ignores leading and trailing whitespace.

    Args:
        text: The text content to analyze.

    Returns:
        Integer word count.
    """
    return len(text.split())


class WordCountInput(BaseModel):
    text: str = Field(description="The text content to analyze for word counting")
    ignore_numbers: bool = Field(
        default=False,
        description="If True, exclude numeric tokens from the word count",
    )
    min_word_length: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Minimum character length for a token to count as a word",
    )


@tool(args_schema=WordCountInput)
def word_counter_v4(
    text: str,
    ignore_numbers: bool = False,
    min_word_length: int = 1,
) -> int:
    """Count words with advanced filtering options.

    Use this tool when the user asks for:
    - Word count excluding numbers
    - Filtering short words
    - Advanced text statistics

    Args:
        text: The text content to analyze.
        ignore_numbers: Skip numeric-only tokens when counting.
        min_word_length: Minimum chars for a token to count (default 1).

    Returns:
        Filtered integer word count.
    """
    tokens = text.split()
    if ignore_numbers:
        tokens = [t for t in tokens if not t.isdigit()]
    if min_word_length > 1:
        tokens = [t for t in tokens if len(t) >= min_word_length]
    return len(tokens)
