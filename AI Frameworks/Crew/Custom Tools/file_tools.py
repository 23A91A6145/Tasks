import csv
import io
import json
from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ReadFileInput(BaseModel):
    path: str = Field(description="Path to the file to read")
    encoding: str = Field(default="utf-8", description="File encoding")


@tool(args_schema=ReadFileInput)
def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read the contents of a file.

    Args:
        path: Path to the file.
        encoding: File encoding.

    Returns:
        File content as a string.
    """
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: file not found: {path}"
        if not p.is_file():
            return f"Error: not a file: {path}"
        return p.read_text(encoding=encoding)
    except Exception as e:
        return f"Error reading file: {e}"


class WriteFileInput(BaseModel):
    path: str = Field(description="Path to write the file")
    content: str = Field(description="Content to write")
    encoding: str = Field(default="utf-8", description="File encoding")


@tool(args_schema=WriteFileInput)
def write_file(path: str, content: str, encoding: str = "utf-8") -> str:
    """Write content to a file.

    Args:
        path: Path to write the file.
        content: Text content to write.
        encoding: File encoding.

    Returns:
        Success or error message.
    """
    try:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding=encoding)
        return f"Successfully wrote {len(content)} bytes to {p}"
    except Exception as e:
        return f"Error writing file: {e}"


class ListDirInput(BaseModel):
    path: str = Field(default=".", description="Directory path to list")
    pattern: str | None = Field(default=None, description="Optional glob pattern (e.g. '*.py')")


@tool(args_schema=ListDirInput)
def list_dir(path: str = ".", pattern: str | None = None) -> str:
    """List files and directories at the given path.

    Args:
        path: Directory path.
        pattern: Optional glob pattern to filter.

    Returns:
        Sorted listing with type and size.
    """
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: path not found: {path}"
        if not p.is_dir():
            return f"Error: not a directory: {path}"
        if pattern:
            items = sorted(p.glob(pattern))
        else:
            items = sorted(p.iterdir())
        lines = []
        for item in items:
            if item.is_dir():
                lines.append(f"  📁 {item.name}/")
            elif item.is_file():
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f}K"
                else:
                    size_str = f"{size/1024/1024:.1f}M"
                lines.append(f"  📄 {item.name} ({size_str})")
            else:
                lines.append(f"  {item.name}")
        if not lines:
            return "Directory is empty."
        header = f"Contents of {p}/ ({len(lines)} items)"
        return header + "\n" + "\n".join(lines)
    except Exception as e:
        return f"Error listing directory: {e}"


class CsvToJsonInput(BaseModel):
    csv_text: str = Field(description="CSV text to convert")
    delimiter: str = Field(default=",", description="CSV delimiter")
    indent: int = Field(default=2, ge=0, le=8, description="JSON indent")


@tool(args_schema=CsvToJsonInput)
def csv_to_json(csv_text: str, delimiter: str = ",", indent: int = 2) -> str:
    """Convert CSV text to JSON string.

    Args:
        csv_text: CSV content.
        delimiter: Column delimiter.
        indent: JSON indentation.

    Returns:
        JSON string.
    """
    try:
        reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return "[]"
        return json.dumps(rows, indent=indent)
    except Exception as e:
        return f"Error converting CSV to JSON: {e}"


class JsonToCsvInput(BaseModel):
    json_text: str = Field(description="JSON text to convert (array of objects)")
    delimiter: str = Field(default=",", description="CSV delimiter")


@tool(args_schema=JsonToCsvInput)
def json_to_csv(json_text: str, delimiter: str = ",") -> str:
    """Convert JSON string to CSV.

    Args:
        json_text: JSON array of objects.
        delimiter: CSV delimiter.

    Returns:
        CSV string.
    """
    try:
        data = json.loads(json_text)
        if not isinstance(data, list) or not data:
            return "Error: JSON must be a non-empty array of objects."
        if not isinstance(data[0], dict):
            return "Error: JSON array elements must be objects."
        headers = list(data[0].keys())
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=delimiter)
        writer.writerow(headers)
        for row in data:
            writer.writerow([row.get(h, "") for h in headers])
        return buf.getvalue().strip()
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {e}"
    except Exception as e:
        return f"Error converting JSON to CSV: {e}"
