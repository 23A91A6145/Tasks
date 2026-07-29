import base64
import io

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CreateBarChartInput(BaseModel):
    labels: list[str] = Field(description="Category labels")
    values: list[float] = Field(description="Numeric values")
    title: str = Field(default="Bar Chart", description="Chart title")
    xlabel: str = Field(default="", description="X-axis label")
    ylabel: str = Field(default="", description="Y-axis label")
    width: int = Field(default=8, ge=4, le=20, description="Figure width in inches")
    height: int = Field(default=5, ge=3, le=16, description="Figure height in inches")


@tool(args_schema=CreateBarChartInput)
def create_bar_chart(labels: list[str], values: list[float], title: str = "Bar Chart",
                      xlabel: str = "", ylabel: str = "", width: int = 8, height: int = 5) -> str:
    """Create a bar chart and return as base64 PNG.

    Args:
        labels: Category labels.
        values: Numeric values.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        width: Figure width.
        height: Figure height.

    Returns:
        Base64-encoded PNG image.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return "Error: matplotlib is required. Install with: pip install crew-tools[charts]"
    try:
        fig, ax = plt.subplots(figsize=(width, height))
        ax.bar(labels, values)
        ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        return f"Error creating chart: {e}"


class CreateLineChartInput(BaseModel):
    x_values: list[float] = Field(description="X-axis values")
    y_values: list[float] = Field(description="Y-axis values")
    title: str = Field(default="Line Chart", description="Chart title")
    xlabel: str = Field(default="", description="X-axis label")
    ylabel: str = Field(default="", description="Y-axis label")
    width: int = Field(default=8, ge=4, le=20)
    height: int = Field(default=5, ge=3, le=16)


@tool(args_schema=CreateLineChartInput)
def create_line_chart(x_values: list[float], y_values: list[float], title: str = "Line Chart",
                       xlabel: str = "", ylabel: str = "", width: int = 8, height: int = 5) -> str:
    """Create a line chart and return as base64 PNG.

    Args:
        x_values: X-axis data points.
        y_values: Y-axis data points.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        width: Figure width.
        height: Figure height.

    Returns:
        Base64-encoded PNG image.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return "Error: matplotlib is required. Install with: pip install crew-tools[charts]"
    try:
        fig, ax = plt.subplots(figsize=(width, height))
        ax.plot(x_values, y_values, marker="o")
        ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        return f"Error creating chart: {e}"


class CreatePieChartInput(BaseModel):
    labels: list[str] = Field(description="Slice labels")
    values: list[float] = Field(description="Slice sizes")
    title: str = Field(default="Pie Chart", description="Chart title")
    width: int = Field(default=8, ge=4, le=20)
    height: int = Field(default=6, ge=3, le=16)


@tool(args_schema=CreatePieChartInput)
def create_pie_chart(labels: list[str], values: list[float], title: str = "Pie Chart",
                      width: int = 8, height: int = 6) -> str:
    """Create a pie chart and return as base64 PNG.

    Args:
        labels: Slice labels.
        values: Slice sizes.
        title: Chart title.
        width: Figure width.
        height: Figure height.

    Returns:
        Base64-encoded PNG image.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return "Error: matplotlib is required. Install with: pip install crew-tools[charts]"
    try:
        fig, ax = plt.subplots(figsize=(width, height))
        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.set_title(title)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        return f"Error creating chart: {e}"


class CreateHistogramInput(BaseModel):
    values: list[float] = Field(description="Data values")
    bins: int = Field(default=10, ge=2, le=100, description="Number of bins")
    title: str = Field(default="Histogram", description="Chart title")
    xlabel: str = Field(default="", description="X-axis label")
    ylabel: str = Field(default="", description="Y-axis label")
    width: int = Field(default=8, ge=4, le=20)
    height: int = Field(default=5, ge=3, le=16)


@tool(args_schema=CreateHistogramInput)
def create_histogram(values: list[float], bins: int = 10, title: str = "Histogram",
                      xlabel: str = "", ylabel: str = "", width: int = 8, height: int = 5) -> str:
    """Create a histogram and return as base64 PNG.

    Args:
        values: Data values.
        bins: Number of bins.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        width: Figure width.
        height: Figure height.

    Returns:
        Base64-encoded PNG image.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return "Error: matplotlib is required. Install with: pip install crew-tools[charts]"
    try:
        fig, ax = plt.subplots(figsize=(width, height))
        ax.hist(values, bins=bins)
        ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        return f"Error creating chart: {e}"
