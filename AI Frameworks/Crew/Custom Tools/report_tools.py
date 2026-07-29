import textwrap

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class MarkdownTableInput(BaseModel):
    headers: list[str] = Field(description="Column headers")
    rows: list[list[str]] = Field(description="Table data as list of row-lists")
    alignment: str = Field(default="left", description="Column alignment: left, center, right")


@tool(args_schema=MarkdownTableInput)
def markdown_table(headers: list[str], rows: list[list[str]], alignment: str = "left") -> str:
    """Create a formatted Markdown table.

    Args:
        headers: Column header names.
        rows: Table data (list of rows, each a list of strings).
        alignment: Column alignment.

    Returns:
        Markdown table string.
    """
    if not headers:
        return "Error: headers required"
    align_map = {"left": ":---", "center": ":---:", "right": "---:"}
    sep = align_map.get(alignment, ":---")

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells):
        return "| " + " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(cells)) + " |"

    lines = [fmt_row(headers)]
    lines.append("|" + "|".join(sep.ljust(w + 2) if alignment != "right" else sep.rjust(w + 2) for w in col_widths) + "|")
    for row in rows:
        padded = [row[i] if i < len(row) else "" for i in range(len(headers))]
        lines.append(fmt_row(padded))

    return "\n".join(lines)


class HtmlTableInput(BaseModel):
    headers: list[str] = Field(description="Column headers")
    rows: list[list[str]] = Field(description="Table data")
    caption: str = Field(default="", description="Optional table caption")
    striped: bool = Field(default=False, description="Add striped row classes")


@tool(args_schema=HtmlTableInput)
def html_table(headers: list[str], rows: list[list[str]], caption: str = "", striped: bool = False) -> str:
    """Create an HTML table from headers and row data.

    Args:
        headers: Column headers.
        rows: Table data.
        caption: Optional caption text.
        striped: Add CSS class 'striped' to odd rows.

    Returns:
        HTML table string.
    """
    if not headers:
        return "Error: headers required"

    buf = ["<table>"]
    if caption:
        buf.append(f"  <caption>{caption}</caption>")
    buf.append("  <thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead>")
    buf.append("  <tbody>")
    for i, row in enumerate(rows):
        cls = ' class="striped"' if striped and i % 2 == 1 else ""
        cells = "".join(f"<td>{c}</td>" for c in row)
        buf.append(f"    <tr{cls}>{cells}</tr>")
    buf.append("  </tbody>")
    buf.append("</table>")
    return "\n".join(buf)


class WordWrapInput(BaseModel):
    text: str = Field(description="Text to wrap")
    width: int = Field(default=70, ge=20, le=120, description="Max line width")
    indent: str = Field(default="", description="Indentation string")


@tool(args_schema=WordWrapInput)
def word_wrap(text: str, width: int = 70, indent: str = "") -> str:
    """Wrap text to a specified line width.

    Args:
        text: Input text.
        width: Max characters per line.
        indent: Optional indentation prefix.

    Returns:
        Wrapped text.
    """
    wrapper = textwrap.TextWrapper(width=width, initial_indent=indent, subsequent_indent=indent)
    try:
        return wrapper.fill(text)
    except Exception as e:
        return f"Error wrapping text: {e}"
