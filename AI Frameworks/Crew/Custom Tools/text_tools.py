import re

from langchain_core.tools import tool
from pydantic import BaseModel, Field


@tool
def count_sentences(*, text: str, delimiters: str = ".!?") -> int:
    """Count the number of sentences in the given text.

    Splits on sentence-ending punctuation (. ! ?) and filters empty strings.

    Args:
        text: The text to analyze.
        delimiters: String of characters that end a sentence (default ".!?").

    Returns:
        Number of sentences.
    """
    pattern = f"[{re.escape(delimiters)}]"
    sentences = [s.strip() for s in re.split(pattern, text) if s.strip()]
    return len(sentences) if sentences else 0


@tool
def reading_time(
    *,
    text: str,
    wpm: int = 200,
    include_headers: bool = True,
) -> float:
    """Estimate reading time for a given text.

    Uses average reading speed in words per minute (wpm).

    Args:
        text: The text to estimate reading time for.
        wpm: Reading speed in words per minute (default 200).
        include_headers: Count header text in word total (default True).

    Returns:
        Reading time in minutes, rounded to 1 decimal.
    """
    if not include_headers:
        lines = [l for l in text.split("\n") if not l.strip().startswith(("#", "---"))]
        text = "\n".join(lines)
    word_count = len(text.split())
    if word_count == 0:
        return 0.0
    return round(word_count / wpm, 1)


class TextStatsInput(BaseModel):
    text: str = Field(description="The text to analyze")
    count_spaces: bool = Field(
        default=False,
        description="Include space characters in character count",
    )
    include_headers: bool = Field(
        default=True,
        description="Include markdown headers in analysis",
    )


@tool(args_schema=TextStatsInput)
def text_stats(
    text: str,
    count_spaces: bool = False,
    include_headers: bool = True,
) -> dict:
    """Compute comprehensive text statistics.

    Returns word count, sentence count, character count,
    average word length, estimated reading time, and paragraph count.

    Args:
        text: The text to analyze.
        count_spaces: Include spaces in char count.
        include_headers: Include header text.

    Returns:
        Dict with stats keys.
    """
    if not include_headers:
        lines = [l for l in text.split("\n") if not l.strip().startswith("#")]
        text = "\n".join(lines)

    words = text.split()
    chars = len(text) if count_spaces else len(text.replace(" ", ""))
    sentences = max(1, len([s for s in re.split(r"[.!?]+", text) if s.strip()]))
    paragraphs = max(1, len([p for p in text.split("\n\n") if p.strip()]))
    avg_word_len = round(sum(len(w) for w in words) / len(words), 2) if words else 0.0
    reading_time_min = round(len(words) / 200, 1)

    return {
        "word_count": len(words),
        "sentence_count": sentences,
        "char_count": chars,
        "avg_word_length": avg_word_len,
        "paragraph_count": paragraphs,
        "reading_time_min": reading_time_min,
    }
