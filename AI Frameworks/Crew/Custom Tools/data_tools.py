import io

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class DescribeDataInput(BaseModel):
    csv_text: str = Field(description="CSV data as text")
    delimiter: str = Field(default=",", description="CSV delimiter")


@tool(args_schema=DescribeDataInput)
def describe_data(csv_text: str, delimiter: str = ",") -> str:
    """Describe a CSV dataset with column statistics.

    Args:
        csv_text: CSV data as a string.
        delimiter: Column delimiter.

    Returns:
        Summary statistics per column.
    """
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas is required. Install with: pip install crew-tools[data]"

    try:
        df = pd.read_csv(io.StringIO(csv_text), delimiter=delimiter)
    except Exception as e:
        return f"Error parsing CSV: {e}"

    if df.empty:
        return "Empty dataset."

    buf = io.StringIO()
    buf.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")
    buf.write(f"Columns: {', '.join(df.columns)}\n\n")

    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols):
        buf.write("Numeric columns:\n")
        desc = df[num_cols].describe().to_dict()
        for col in num_cols:
            d = desc[col]
            buf.write(f"  {col}: count={d['count']:.0f}, mean={d['mean']:.3f}, "
                      f"std={d['std']:.3f}, min={d['min']:.3f}, "
                      f"25%={d['25%']:.3f}, 50%={d['50%']:.3f}, "
                      f"75%={d['75%']:.3f}, max={d['max']:.3f}\n")
        buf.write("\n")

    cat_cols = df.select_dtypes(exclude="number").columns
    if len(cat_cols):
        buf.write("Categorical columns:\n")
        for col in cat_cols:
            nunique = df[col].nunique()
            top = df[col].mode().iloc[0] if nunique > 0 else "N/A"
            buf.write(f"  {col}: {nunique} unique, top={top}\n")

    return buf.getvalue().strip()


class FilterRowsInput(BaseModel):
    csv_text: str = Field(description="CSV data as text")
    column: str = Field(description="Column to filter on")
    op: str = Field(default="eq", description="Comparison: eq, ne, gt, ge, lt, le, contains")
    value: str = Field(description="Value to compare against")
    delimiter: str = Field(default=",", description="CSV delimiter")


@tool(args_schema=FilterRowsInput)
def filter_rows(csv_text: str, column: str, op: str, value: str, delimiter: str = ",") -> str:
    """Filter CSV rows based on a column condition.

    Args:
        csv_text: CSV data.
        column: Column name.
        op: Comparison operator (eq, ne, gt, ge, lt, le, contains).
        value: Value to compare.
        delimiter: CSV delimiter.

    Returns:
        Filtered CSV as text.
    """
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas is required. Install with: pip install crew-tools[data]"

    try:
        df = pd.read_csv(io.StringIO(csv_text), delimiter=delimiter)
    except Exception as e:
        return f"Error parsing CSV: {e}"

    if column not in df.columns:
        return f"Error: column '{column}' not found. Available: {', '.join(df.columns)}"

    ops = {"eq": "==", "ne": "!=", "gt": ">", "ge": ">=", "lt": "<", "le": "<="}
    try:
        if op == "contains":
            mask = df[column].astype(str).str.contains(value, na=False)
        elif op in ops:
            col_series = pd.to_numeric(df[column], errors="coerce")  # noqa: F841 — used in eval
            val_num = float(value)  # noqa: F841 — used in eval
            op_sym = ops[op]
            mask = eval(f"col_series {op_sym} val_num")
        else:
            return f"Error: unknown operator '{op}'. Use: eq, ne, gt, ge, lt, le, contains"
    except Exception as e:
        return f"Error applying filter: {e}"

    result = df[mask]
    if result.empty:
        return "No matching rows."
    return result.to_csv(index=False)


class SortRowsInput(BaseModel):
    csv_text: str = Field(description="CSV data as text")
    column: str = Field(description="Column to sort by")
    ascending: bool = Field(default=True, description="Sort ascending (True) or descending (False)")
    delimiter: str = Field(default=",", description="CSV delimiter")


@tool(args_schema=SortRowsInput)
def sort_rows(csv_text: str, column: str, ascending: bool = True, delimiter: str = ",") -> str:
    """Sort CSV rows by a column.

    Args:
        csv_text: CSV data.
        column: Column to sort by.
        ascending: Sort direction.
        delimiter: CSV delimiter.

    Returns:
        Sorted CSV as text.
    """
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas is required. Install with: pip install crew-tools[data]"

    try:
        df = pd.read_csv(io.StringIO(csv_text), delimiter=delimiter)
    except Exception as e:
        return f"Error parsing CSV: {e}"

    if column not in df.columns:
        return f"Error: column '{column}' not found. Available: {', '.join(df.columns)}"

    try:
        result = df.sort_values(by=column, ascending=ascending)
    except Exception as e:
        return f"Error sorting: {e}"

    return result.to_csv(index=False)


class AggregateDataInput(BaseModel):
    csv_text: str = Field(description="CSV data as text")
    group_by: str = Field(description="Column to group by")
    agg_column: str = Field(description="Column to aggregate")
    agg_func: str = Field(default="mean", description="Aggregation: mean, sum, count, min, max, std, median")
    delimiter: str = Field(default=",", description="CSV delimiter")


@tool(args_schema=AggregateDataInput)
def aggregate_data(csv_text: str, group_by: str, agg_column: str, agg_func: str = "mean", delimiter: str = ",") -> str:
    """Aggregate CSV data by grouping a column and applying a function.

    Args:
        csv_text: CSV data.
        group_by: Column to group by.
        agg_column: Column to aggregate.
        agg_func: Aggregation function: mean, sum, count, min, max, std, median.
        delimiter: CSV delimiter.

    Returns:
        Aggregated CSV as text.
    """
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas is required. Install with: pip install crew-tools[data]"

    try:
        df = pd.read_csv(io.StringIO(csv_text), delimiter=delimiter)
    except Exception as e:
        return f"Error parsing CSV: {e}"

    if group_by not in df.columns:
        return f"Error: group_by column '{group_by}' not found. Available: {', '.join(df.columns)}"
    if agg_column not in df.columns:
        return f"Error: agg_column '{agg_column}' not found. Available: {', '.join(df.columns)}"

    allowed = {"mean", "sum", "count", "min", "max", "std", "median"}
    if agg_func not in allowed:
        return f"Error: unknown aggregation '{agg_func}'. Use: {', '.join(sorted(allowed))}"

    try:
        result = df.groupby(group_by)[agg_column].agg(agg_func).reset_index()
    except Exception as e:
        return f"Error aggregating: {e}"

    return result.to_csv(index=False)
