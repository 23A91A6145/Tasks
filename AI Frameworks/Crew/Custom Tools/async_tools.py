import asyncio

from langchain_core.tools import tool

from crew_tools.production import async_batch_process

LENGTH = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
}


@tool
async def async_word_counter(text: str) -> str:
    """Count words asynchronously.

    Args:
        text: The text to count words in.

    Returns:
        Word count as a string.
    """
    await asyncio.sleep(0)
    if not text or not text.strip():
        return "0"
    return str(len(text.split()))


@tool
async def async_convert(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a length measurement asynchronously.

    Args:
        value: Numeric value to convert.
        from_unit: Source unit (mm, cm, m, km, in, ft, yd, mi).
        to_unit: Target unit (mm, cm, m, km, in, ft, yd, mi).

    Returns:
        Converted value as a string.
    """
    await asyncio.sleep(0)
    fu = from_unit.lower()
    tu = to_unit.lower()
    if fu not in LENGTH:
        return f"Error: unknown unit '{from_unit}'"
    if tu not in LENGTH:
        return f"Error: unknown unit '{to_unit}'"
    result = value * LENGTH[fu] / LENGTH[tu]
    return f"{round(result, 6)}"


@tool
async def async_calculate(a: float, b: float = 0.0, op: str = "add") -> str:
    """Perform arithmetic asynchronously.

    Args:
        a: First number.
        b: Second number (default 0).
        op: Operation: add, sub, mul, div, pow, mod (default add).

    Returns:
        Result as a string.
    """
    await asyncio.sleep(0)
    op = {"divide": "div", "multiply": "mul", "subtract": "sub", "addition": "add"}.get(op, op)
    ops = {
        "add": a + b,
        "sub": a - b,
        "mul": a * b,
        "div": a / b if b != 0 else None,
        "pow": a ** b,
        "mod": a % b if b != 0 else None,
    }
    if op not in ops:
        return f"Error: unknown op '{op}'"
    result = ops[op]
    if result is None:
        return "Error: division by zero"
    return str(result)


async def async_batch_word_counter(texts: list[str], max_concurrency: int = 5) -> list[str]:
    """Count words in multiple texts concurrently.

    Args:
        texts: List of text strings.
        max_concurrency: Max parallel executions.

    Returns:
        List of word counts.
    """
    inputs = [{"text": t} for t in texts]
    return await async_batch_process(async_word_counter, inputs, max_concurrency)


async def async_batch_convert(conversions: list[dict], max_concurrency: int = 5) -> list[str]:
    """Convert multiple measurements concurrently.

    Args:
        conversions: List of dicts with value, from_unit, to_unit keys.
        max_concurrency: Max parallel executions.

    Returns:
        List of conversion results.
    """
    return await async_batch_process(async_convert, conversions, max_concurrency)
