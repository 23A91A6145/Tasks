import statistics

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class BasicStatsInput(BaseModel):
    values: list[float] = Field(description="List of numeric values")


@tool(args_schema=BasicStatsInput)
def basic_stats(values: list[float]) -> str:
    """Compute basic statistics for a list of numbers.

    Args:
        values: Numeric data.

    Returns:
        Formatted statistics: count, min, max, mean, median, std, variance.
    """
    if not values:
        return "Error: empty list"
    try:
        n = len(values)
        mn = min(values)
        mx = max(values)
        mean = statistics.mean(values)
        median = statistics.median(values)
        stdev = statistics.stdev(values) if n > 1 else 0.0
        var = statistics.variance(values) if n > 1 else 0.0
        return (
            f"Count: {n}\n"
            f"Min: {mn:.4f}\n"
            f"Max: {mx:.4f}\n"
            f"Mean: {mean:.4f}\n"
            f"Median: {median:.4f}\n"
            f"Std Dev: {stdev:.4f}\n"
            f"Variance: {var:.4f}"
        )
    except Exception as e:
        return f"Error computing statistics: {e}"


class MovingAverageInput(BaseModel):
    values: list[float] = Field(description="List of numeric values")
    window: int = Field(default=3, ge=2, le=100, description="Window size")


@tool(args_schema=MovingAverageInput)
def moving_average(values: list[float], window: int = 3) -> str:
    """Compute the moving average of a numeric series.

    Args:
        values: Numeric data.
        window: Window size.

    Returns:
        Moving average values as JSON list.
    """
    if len(values) < window:
        return f"Error: need at least {window} values, got {len(values)}"
    try:
        result = []
        for i in range(len(values) - window + 1):
            avg = sum(values[i:i + window]) / window
            result.append(round(avg, 4))
        import json
        return json.dumps(result)
    except Exception as e:
        return f"Error computing moving average: {e}"


class PercentileInput(BaseModel):
    values: list[float] = Field(description="List of numeric values")
    percentiles: list[float] = Field(default=[25, 50, 75], description="Percentiles to compute (0-100)")


@tool(args_schema=PercentileInput)
def percentile(values: list[float], percentiles: list[float] | None = None) -> str:
    """Compute percentiles for a list of numbers.

    Args:
        values: Numeric data.
        percentiles: List of percentile values.

    Returns:
        Formatted percentile results.
    """
    if percentiles is None:
        percentiles = [25, 50, 75]
    if not values:
        return "Error: empty list"
    try:
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        lines = []
        for p in percentiles:
            idx = max(0, min(n - 1, round(p / 100 * (n - 1))))
            lines.append(f"P{p}: {sorted_vals[idx]:.4f}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error computing percentiles: {e}"


class OutliersInput(BaseModel):
    values: list[float] = Field(description="List of numeric values")
    method: str = Field(default="iqr", description="Method: iqr (1.5*IQR) or zscore (|z|>3)")


@tool(args_schema=OutliersInput)
def outliers(values: list[float], method: str = "iqr") -> str:
    """Detect outliers in a list of numbers.

    Args:
        values: Numeric data.
        method: Detection method (iqr or zscore).

    Returns:
        Outlier values and indices.
    """
    if len(values) < 4:
        return "Error: need at least 4 values"
    try:
        if method == "iqr":
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            q1_idx = max(0, min(n - 1, round(0.25 * (n - 1))))
            q3_idx = max(0, min(n - 1, round(0.75 * (n - 1))))
            q1 = sorted_vals[q1_idx]
            q3 = sorted_vals[q3_idx]
            iqr_val = q3 - q1
            lower = q1 - 1.5 * iqr_val
            upper = q3 + 1.5 * iqr_val
            found = [(i, v) for i, v in enumerate(values) if v < lower or v > upper]
        elif method == "zscore":
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            found = [(i, v) for i, v in enumerate(values) if abs(v - mean) > 3 * stdev]
        else:
            return "Error: method must be 'iqr' or 'zscore'"

        if not found:
            return "No outliers detected."
        import json
        result = [{"index": i, "value": round(v, 4)} for i, v in found]
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error detecting outliers: {e}"
