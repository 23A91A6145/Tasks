import difflib
import re

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class RenderTemplateInput(BaseModel):
    template: str = Field(description="Jinja2 template string")
    values: dict = Field(default_factory=dict, description="Template variable values")


@tool(args_schema=RenderTemplateInput)
def render_template(template: str, values: dict | None = None) -> str:
    """Render a Jinja2 template with provided variables.

    Args:
        template: The Jinja2 template string.
        values: Dict of variable names to values.

    Returns:
        Rendered template output.
    """
    if values is None:
        values = {}
    try:
        from jinja2 import Template, TemplateSyntaxError, UndefinedError
    except ImportError:
        return "Error: jinja2 is required. Install with: pip install crew-tools[templates]"
    try:
        t = Template(template)
        return t.render(**values)
    except TemplateSyntaxError as e:
        return f"Error: template syntax error at line {e.lineno}: {e.message}"
    except UndefinedError as e:
        return f"Error: undefined variable: {e}"
    except Exception as e:
        return f"Error rendering template: {e}"


class RegexSearchInput(BaseModel):
    text: str = Field(description="Text to search in")
    pattern: str = Field(description="Regex pattern")
    flags: str = Field(default="", description="Regex flags: i=IGNORECASE, m=MULTILINE, s=DOTALL")


@tool(args_schema=RegexSearchInput)
def regex_search(text: str, pattern: str, flags: str = "") -> str:
    """Search for regex matches in text.

    Args:
        text: Text to search.
        pattern: Regex pattern.
        flags: Optional flags (i=IGNORECASE, m=MULTILINE, s=DOTALL).

    Returns:
        Formatted list of matches.
    """
    try:
        re_flags = 0
        if "i" in flags:
            re_flags |= re.IGNORECASE
        if "m" in flags:
            re_flags |= re.MULTILINE
        if "s" in flags:
            re_flags |= re.DOTALL
        matches = re.findall(pattern, text, re_flags)
    except re.error as e:
        return f"Error: invalid regex: {e}"

    if not matches:
        return "No matches found."

    lines = []
    for i, m in enumerate(matches, 1):
        if isinstance(m, tuple):
            m = ", ".join(str(g) for g in m)
        lines.append(f"{i}. {m}")
    return "\n".join(lines)


class RegexReplaceInput(BaseModel):
    text: str = Field(description="Text to perform replacement on")
    pattern: str = Field(description="Regex pattern")
    replacement: str = Field(description="Replacement string")
    count: int = Field(default=0, ge=0, description="Max replacements (0 = all)")
    flags: str = Field(default="", description="Regex flags: i=IGNORECASE, m=MULTILINE, s=DOTALL")


@tool(args_schema=RegexReplaceInput)
def regex_replace(text: str, pattern: str, replacement: str, count: int = 0, flags: str = "") -> str:
    """Replace regex matches in text.

    Args:
        text: Text to modify.
        pattern: Regex pattern.
        replacement: Replacement string.
        count: Max replacements (0 = all).
        flags: Optional flags.

    Returns:
        Modified text.
    """
    try:
        re_flags = 0
        if "i" in flags:
            re_flags |= re.IGNORECASE
        if "m" in flags:
            re_flags |= re.MULTILINE
        if "s" in flags:
            re_flags |= re.DOTALL
        result = re.sub(pattern, replacement, text, count=count or 0, flags=re_flags)
    except re.error as e:
        return f"Error: invalid regex: {e}"
    return result


class DiffTextInput(BaseModel):
    text_a: str = Field(description="Original text")
    text_b: str = Field(description="Modified text")
    context_lines: int = Field(default=3, ge=0, le=10, description="Context lines in unified diff")


@tool(args_schema=DiffTextInput)
def diff_text(text_a: str, text_b: str, context_lines: int = 3) -> str:
    """Generate a unified diff between two texts.

    Args:
        text_a: Original text.
        text_b: Modified text.
        context_lines: Lines of context.

    Returns:
        Unified diff string.
    """
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    diff = difflib.unified_diff(lines_a, lines_b, fromfile="a", tofile="b", n=context_lines)
    result = "".join(diff)
    if not result:
        return "Texts are identical."
    return result
