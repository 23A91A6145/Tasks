"""
Crew Tools UI — Production-grade Streamlit interface for all 81 tools.

Usage:
    crew-tools streamlit
    streamlit run crew_tools/ui/streamlit_app.py
"""

import asyncio
import base64
import json
import os
import re
import sys
import time
from collections import Counter
from typing import Any

_this_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st

from crew_tools import TOOL_REGISTRY

st.set_page_config(
    page_title="Crew Tools",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "### Crew Tools v0.1.0\n81 LangChain-compatible AI tools.\n3 interfaces · 439 tests · 87% coverage",
        "Report a bug": "https://github.com/anomalyco/crew-tools/issues",
    },
)

# ── Master CSS: Dark + Light with glassmorphism ────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
code, pre, .stCodeBlock, .stCode { font-family: 'JetBrains Mono', monospace !important; }

/* ── Base Theme ── */
:root {
    --bg-primary: #0b0f1a;
    --bg-secondary: #111827;
    --bg-card: #1a1f2e;
    --bg-hover: #232a3b;
    --border: #1e2d4a;
    --border-light: #2a3a5a;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent: #6366f1;
    --accent-glow: rgba(99,102,241,0.3);
    --accent-gradient: linear-gradient(135deg, #6366f1, #a855f7);
    --success: #22c55e;
    --warning: #f59e0b;
    --error: #ef4444;
    --radius: 12px;
    --radius-sm: 8px;
    --shadow: 0 4px 24px rgba(0,0,0,0.3);
}

/* ── Layout ── */
.stApp { background: var(--bg-primary); }
.stSidebar { background: var(--bg-secondary) !important; border-right: 1px solid var(--border) !important; }
.sidebar-content { background: var(--bg-secondary); }

/* ── Glassmorphism Cards ── */
.glass {
    background: linear-gradient(135deg, rgba(26,31,46,0.9), rgba(26,31,46,0.7));
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

/* ── Title + Headers ── */
h1 { font-size: 2rem !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
h2 { font-size: 1.4rem !important; font-weight: 600 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; color: var(--text-secondary) !important; }

/* ── Buttons ── */
.stButton button {
    background: var(--accent-gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 500 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px var(--accent-glow) !important;
}
.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px var(--accent-glow) !important;
}
.stButton button:active { transform: translateY(0) !important; }
button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}
button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--text-primary) !important;
}

/* ── Inputs ── */
.stTextInput>div>div>input,
.stTextArea textarea,
.stSelectbox>div>div>select,
.stNumberInput input {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.6rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput>div>div>input:focus,
.stTextArea textarea:focus,
.stSelectbox>div>div>select:focus,
.stNumberInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm);
    padding: 0.5rem 1.2rem;
    color: var(--text-secondary);
    transition: all 0.2s;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-gradient) !important;
    color: white !important;
}

/* ── Expanders ── */
div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin: 0.4rem 0;
    overflow: hidden;
}
div[data-testid="stExpander"] > div[role="button"] {
    background: transparent !important;
    padding: 0.6rem 1rem !important;
}
div[data-testid="stExpander"] > div[role="button"] p {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    transition: border-color 0.2s;
}
div[data-testid="stMetric"]:hover { border-color: var(--accent); }
div[data-testid="stMetric"] label { color: var(--text-muted) !important; font-size: 0.8rem !important; }
div[data-testid="stMetric"] div { color: var(--text-primary) !important; font-size: 1.5rem !important; font-weight: 700 !important; }

/* ── Alerts / Info / Error ── */
.stAlert { border-radius: var(--radius-sm) !important; border: none !important; }
.st-ae { background: var(--bg-card) !important; border-radius: var(--radius) !important; border: 1px solid var(--border) !important; }
.stCodeBlock { background: var(--bg-primary) !important; border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important; }
.stSpinner > div { border-color: var(--accent) !important; border-right-color: transparent !important; }
.stMarkdown p { color: var(--text-primary) !important; }
.stMarkdown a { color: var(--accent) !important; }

/* ── Sidebar ── */
.stSidebar .stButton button {
    background: transparent !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0.4rem 0.8rem !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
    transition: all 0.15s !important;
}
.stSidebar .stButton button:hover {
    background: var(--bg-hover) !important;
    color: var(--text-primary) !important;
}
.stSidebar .stButton button[kind="secondary"] {
    padding: 0.2rem 0.4rem !important;
    font-size: 1rem !important;
}

/* ── Dividers ── */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ── Badge / Chip ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}

/* ── Tool cards in sidebar ── */
.tool-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 4px 3px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    border: 1px solid transparent;
    margin: 1px 0;
}
.tool-chip:hover {
    border-color: var(--accent);
    background: var(--bg-hover);
}

/* ── Checkbox ── */
.stCheckbox label { color: var(--text-secondary) !important; }

/* ── File uploader ── */
div[data-testid="stFileUploader"] { border: 1px dashed var(--border); border-radius: var(--radius); padding: 1rem; }

/* ── Tooltip custom ── */
div[data-baseweb="tooltip"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; }
</style>
"""

CATEGORIES: dict[str, list[str]] = {
    "Text & Language": ["word_counter_v1","word_counter_v2","word_counter_v3","word_counter_v4","word_counter_safe","word_counter_advanced","text_stats","count_sentences","reading_time","diff_text"],
    "Math & Stats": ["calculate_v1","calculate_v2","calculate_v3","calculate_v4","calculate_v5","calculate_safe","basic_stats","percentile","moving_average","outliers"],
    "Conversion": ["convert_v1","convert_v2","convert_v3","convert_v4","convert_safe","timezone_convert","format_date","parse_date","current_time"],
    "Validation": ["validate_email","validate_url","validate_phone","validate_v2","validate_json"],
    "Web & Network": ["web_fetch","web_search","rss_parse","dns_lookup","port_check","http_status"],
    "File & Data": ["read_file","write_file","list_dir","csv_to_json","json_to_csv","describe_data","filter_rows","sort_rows","aggregate_data"],
    "Code": ["run_python","format_code"],
    "Crypto": ["hash_string","base64_encode","base64_decode","random_password"],
    "Templates & Format": ["render_template","regex_search","regex_replace","json_prettify","yaml_parse","yaml_dump","toml_parse","xml_parse","markdown_table","html_table","word_wrap"],
    "Charts": ["create_bar_chart","create_line_chart","create_pie_chart","create_histogram"],
    "System": ["system_info","os_info","which_program","env_get"],
    "Memory": ["session_set","session_get","session_list","session_clear"],
    "Async": ["async_calculate","async_convert","async_word_counter"],
}

CAT_ICONS = {
    "Text & Language": "📝", "Math & Stats": "🔢", "Conversion": "📐",
    "Validation": "✅", "Web & Network": "🌐", "File & Data": "📁",
    "Code": "💻", "Crypto": "🔐", "Templates & Format": "📄",
    "Charts": "📊", "System": "⚙️", "Memory": "🧠", "Async": "⚡",
}

CAT_COLORS = {
    "Text & Language": "#3b82f6", "Math & Stats": "#10b981",
    "Conversion": "#f59e0b", "Validation": "#8b5cf6",
    "Web & Network": "#06b6d4", "File & Data": "#14b8a6",
    "Code": "#f97316", "Crypto": "#ef4444",
    "Templates & Format": "#ec4899", "Charts": "#a855f7",
    "System": "#6b7280", "Memory": "#84cc16", "Async": "#6366f1",
}

TOOL_TO_CATEGORY: dict[str, str] = {}
for cat, names in CATEGORIES.items():
    for n in names:
        TOOL_TO_CATEGORY[n] = cat

EXAMPLES: dict[str, dict[str, Any]] = {
    "word_counter_v1": {"text": "hello world"},
    "word_counter_v2": {"text": "count these words"},
    "word_counter_v3": {"text": "this is a sentence"},
    "word_counter_v4": {"text": "42 is a number", "ignore_numbers": True, "min_word_length": 2},
    "word_counter_safe": {"text": "safe counting"},
    "word_counter_advanced": {"text": "advanced counting", "ignore_numbers": False, "min_word_length": 1},
    "diff_text": {"text_a": "Hello world\nLine two", "text_b": "Hello world\nLine two edited\nLine three"},
    "calculate_v1": {"expression": "2 + 2"},
    "calculate_v2": {"a": 10, "b": 3, "op": "add"},
    "calculate_v3": {"a": 10, "b": 3, "op": "mul"},
    "calculate_v4": {"a": 10, "b": 3, "op": "divide"},
    "calculate_v5": {"expression": "2 + 2", "precision": 2, "safe_mode": True},
    "calculate_safe": {"a": 15.0, "b": 4.0, "op": "multiply"},
    "basic_stats": {"values": [12, 15, 14, 10, 18, 20, 13, 11, 16, 14]},
    "percentile": {"values": [1,2,3,4,5,6,7,8,9,10], "percentiles": [25,50,75,90]},
    "outliers": {"values": [10,12,11,13,14,500,9,11,10], "method": "iqr"},
    "moving_average": {"values": [1, 2, 3, 4, 5], "window": 3},
    "convert_v1": {"value": 10, "from_unit": "km", "to_unit": "m", "category": "length"},
    "convert_v2": {"value": 100, "from_unit": "kg", "to_unit": "lb", "category": "weight"},
    "convert_v3": {"value": 0, "from_unit": "celsius", "to_unit": "fahrenheit", "category": "temperature"},
    "convert_v4": {"value": 5, "from_unit": "mi", "to_unit": "km", "category": "length"},
    "convert_safe": {"value": 5.0, "from_unit": "km", "to_unit": "mi", "category": "length"},
    "timezone_convert": {"date_string": "2024-01-15 14:00:00", "from_tz": "America/New_York", "to_tz": "Asia/Tokyo", "fmt": "%Y-%m-%d %H:%M:%S"},
    "current_time": {"timezone": "UTC", "output_format": "%Y-%m-%d %H:%M:%S %Z"},
    "format_date": {"date_string": "2024-01-15", "output_format": "%Y-%m-%d"},
    "parse_date": {"date_string": "2024-01-15"},
    "validate_json": {"value": '{"name":"Alice","age":30,"active":true}'},
    "validate_email": {"email": "user@example.com"},
    "validate_url": {"url": "https://github.com/anomalyco/crew-tools"},
    "validate_phone": {"phone": "+1-555-123-4567"},
    "validate_v2": {"value": "hello@example.com", "validator_type": "email", "country": "US"},
    "filter_rows": {"csv_text": "name,age\nAlice,30\nBob,25\nCharlie,35", "column": "age", "op": "gt", "value": "28"},
    "sort_rows": {"csv_text": "name,age\nAlice,30\nBob,25\nCharlie,35", "column": "age", "ascending": True},
    "aggregate_data": {"csv_text": "dept,salary\nIT,70000\nIT,80000\nHR,50000\nHR,55000", "group_by": "dept", "agg_column": "salary", "agg_func": "mean"},
    "describe_data": {"csv_text": "x,y\n1,2\n3,4", "delimiter": ","},
    "csv_to_json": {"csv_text": "name,age\nAlice,30\nBob,25", "delimiter": ",", "indent": 2},
    "json_to_csv": {"json_text": '[{"name":"Alice","age":30}]', "delimiter": ","},
    "read_file": {"path": "/tmp/crew_test.txt", "encoding": "utf-8"},
    "write_file": {"path": "/tmp/crew_test.txt", "content": "hello", "encoding": "utf-8"},
    "list_dir": {"path": ".", "pattern": "*.py"},
    "run_python": {"code": "print('Hello from Crew Tools!')", "timeout": 5},
    "format_code": {"code": "def foo(x):\n  return x+1\n", "line_length": 88},
    "hash_string": {"value": "Hello Crew Tools!", "algorithm": "sha256"},
    "base64_encode": {"value": "Hello Crew Tools!"},
    "base64_decode": {"value": "SGVsbG8gQ3JldyBUb29scyE="},
    "random_password": {"length": 16, "special_chars": True},
    "render_template": {"template": "Hello {{ name }}! Today is {{ date }}.", "values": {"name": "World", "date": "2024-01-15"}},
    "regex_search": {"text": "Contact: alice@example.com or bob@test.org", "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"},
    "regex_replace": {"text": "Call 555-1234 or 555-5678 for help", "pattern": r"\d{3}-\d{4}", "replacement": "[REDACTED]"},
    "json_prettify": {"json_text": '{"name":"Alice","age":30,"address":{"city":"NYC","zip":"10001"}}', "indent": 2},
    "yaml_parse": {"yaml_text": "name: Alice\nage: 30\nskills:\n  - Python\n  - Rust"},
    "yaml_dump": {"json_text": '{"name":"Alice","age":30,"skills":["Python","Rust"]}'},
    "toml_parse": {"toml_text": "[server]\nhost = \"localhost\"\nport = 8080\n[server.auth]\nenabled = true"},
    "xml_parse": {"xml_text": "<root><item id='1'>Hello</item><item id='2'>World</item></root>"},
    "markdown_table": {"headers": ["Name","Age","City"], "rows": [["Alice","30","NYC"],["Bob","25","LA"]]},
    "html_table": {"headers": ["Name","Age"], "rows": [["Alice","30"],["Bob","25"]], "caption": "Team Members", "striped": True},
    "word_wrap": {"text": "This is a long text that needs to be wrapped at a specific column width.", "width": 40},
    "create_bar_chart": {"labels": ["A","B","C","D","E"], "values": [10,25,15,30,20], "title": "Sales by Quarter"},
    "create_line_chart": {"x_values": [1,2,3,4,5], "y_values": [10,25,15,30,20], "title": "Trend Analysis"},
    "create_pie_chart": {"labels": ["Sales","Marketing","Engineering","HR"], "values": [30,20,25,10], "title": "Department Budget"},
    "create_histogram": {"values": [1,2,2,3,3,3,4,4,4,4,5,5,5,6,7,8], "bins": 5, "title": "Distribution"},
    "env_get": {"key": "HOME"},
    "session_set": {"key": "username", "value": "crew_user"},
    "session_get": {"key": "test"},
    "session_list": {},
    "session_clear": {},
    "system_info": {},
    "os_info": {},
    "which_program": {"program": "python3"},
    "dns_lookup": {"hostname": "example.com", "record_type": "A"},
    "port_check": {"hostname": "example.com", "port": 80, "timeout": 3.0},
    "http_status": {"url": "https://example.com", "timeout": 10},
    "web_fetch": {"url": "https://example.com", "timeout": 10},
    "web_search": {"query": "python programming", "max_results": 5},
    "rss_parse": {"url": "https://example.com/rss", "max_entries": 5},
    "count_sentences": {"text": "Hello world. How are you?", "delimiters": ".!?"},
    "reading_time": {"text": "some text here for reading", "wpm": 200, "include_headers": True},
    "text_stats": {"text": "Hello world. This is a test.", "count_spaces": False, "include_headers": True},
    "async_calculate": {"a": 10, "b": 3, "op": "divide"},
    "async_convert": {"value": 1, "from_unit": "km", "to_unit": "m"},
    "async_word_counter": {"text": "Hello world from async tool!"},
}


def init_session():
    for key, default in [("selected_tool", None), ("theme", "dark"),
                          ("history", []), ("favorites", set()),
                          ("recent_tools", []), ("usage_count", Counter()),
                          ("copy_count", 0), ("show_welcome", True)]:
        if key not in st.session_state:
            st.session_state[key] = default


def get_schema(name: str) -> dict | None:
    tool = TOOL_REGISTRY.get(name)
    if tool and hasattr(tool, "args_schema") and tool.args_schema:
        try:
            return tool.args_schema.model_json_schema()
        except Exception:
            return None
    return None


def guess_widget(fs: dict) -> str:
    t = fs.get("type")
    if t is None: return "text"
    if "enum" in fs: return "select"
    if t == "boolean": return "checkbox"
    if t in ("integer", "number"): return "number"
    if t == "array": return "array"
    return "text"


def is_multiline(name: str, fs: dict) -> bool:
    keywords = ("text", "code", "csv", "json", "yaml", "xml", "template", "expression")
    if any(k in name.lower() for k in keywords): return True
    return bool(fs.get("maxLength", 0) and fs["maxLength"] > 100)


def field_widget(fname: str, fs: dict, prefix: str) -> Any:
    label = fname.replace("_", " ").title()
    default = fs.get("default")
    desc = fs.get("description", "")
    wt = guess_widget(fs)
    key = f"{prefix}_{fname}"
    ex = st.session_state.get("_example", False)
    if ex and prefix in EXAMPLES and fname in EXAMPLES[prefix]:
        default = EXAMPLES[prefix][fname]
    if "enum" in fs:
        opts = fs["enum"]
        idx = opts.index(default) if default in opts else 0
        return st.selectbox(label, opts, idx, help=desc, key=key)
    if wt == "checkbox":
        return st.checkbox(label, bool(default) if default is not None else False, help=desc, key=key)
    if wt == "number":
        is_int = fs.get("type") == "integer"
        mn, mx = fs.get("minimum"), fs.get("maximum")
        step = 1 if is_int else 0.1
        cur = default if default is not None else (mn or 0)
        if mn is not None and mx is not None:
            return st.slider(label, mn, mx, cur if cur else 50, step, help=desc, key=key)
        fmt = "%d" if is_int else "%.4f"
        return st.number_input(label, cur, step=step, min_value=mn, max_value=mx, help=desc, key=key, format=fmt)
    if is_multiline(fname, fs):
        ml = fs.get("maxLength", 500)
        h = min(max(3, ml // 80), 15)
        cur = default if default else ""
        if isinstance(cur, (list, dict)): cur = json.dumps(cur, indent=2)
        return st.text_area(label, str(cur), height=h, help=desc, key=key)
    cur = default if default else ""
    if isinstance(cur, (list, dict)): cur = json.dumps(cur)
    return st.text_input(label, str(cur), help=desc, key=key)


def detect_chart(output: str) -> str | None:
    if re.match(r"^data:image/png;base64,", output): return "png"
    if re.match(r"^[A-Za-z0-9+/=]{150,}$", output):
        try:
            base64.b64decode(output)
            return "raw"
        except Exception:
            return None
    return None


def is_async_tool(name: str) -> bool:
    t = TOOL_REGISTRY.get(name)
    return t is not None and hasattr(t, "coroutine") and t.coroutine is not None


def _clean_error(e: Exception) -> str:
    msg = str(e)
    lines = msg.split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("For further information"):
            continue
        if stripped.startswith("1 validation error"):
            continue
        if "Input should be" in stripped or "Field required" in stripped or stripped and not stripped.startswith((" ", "\t")):
            out.append(stripped)
    if not out:
        out.append(msg[:200])
    return "Error: " + " | ".join(out)

def invoke_tool(name: str, params: dict) -> tuple[Any, float]:
    t = TOOL_REGISTRY[name]
    start = time.perf_counter()
    try:
        if is_async_tool(name):
            result = asyncio.run(t.ainvoke(params))
        else:
            result = t.invoke(params)
    except Exception as e:
        result = _clean_error(e)
    elapsed = time.perf_counter() - start
    return result, elapsed


def render_output(name: str, output: str):
    chart = detect_chart(output)
    if chart:
        img = output if chart == "png" else f"data:image/png;base64,{output}"
        st.image(img, use_container_width=True)
        raw = output if chart == "raw" else output.split(",")[1]
        st.download_button("📥 Download PNG", base64.b64decode(raw),
                          f"{name}.png", "image/png", type="secondary")
        return
    if output.strip().startswith("Error"):
        st.error(output)
        return
    is_json = False
    cleaned = output.strip()
    try:
        json.loads(cleaned)
        is_json = True
    except Exception:
        try:
            json.loads(cleaned.replace("'", '"'))
            is_json = True
        except Exception:
            is_json = False
    ot = st.tabs(["👁 Preview", "📋 Raw"])
    with ot[0]:
        if is_json:
            st.json(output)
        elif output.startswith(("|", "#", "---", "+-", "<table")):
            st.markdown(output)
        else:
            try:
                st.code(output, line_numbers=True)
            except Exception:
                st.text(output)
    with ot[1]:
        st.code(output, line_numbers=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0.5rem 0.5rem;">
            <div style="font-size:3rem;font-weight:800;background:var(--accent-gradient);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 letter-spacing:-0.03em;">⚡ Crew</div>
            <div style="font-size:1.2rem;font-weight:500;color:var(--text-muted);
                 letter-spacing:-0.01em;margin-top:-4px;">Tools</div>
            <div style="margin-top:8px;display:flex;gap:6px;justify-content:center;flex-wrap:wrap;">
                <span class="badge" style="background:var(--accent);color:white;">v0.1.0</span>
                <span class="badge" style="background:#1e293b;color:var(--text-secondary);">81 tools</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        q = st.text_input("🔍", placeholder="Search tools...", key="sq", label_visibility="collapsed").strip().lower()
        fav_only = st.checkbox("⭐ Favorites only", key="favf")

        if st.session_state.recent_tools:
            with st.expander("🕐 Recent", expanded=False):
                for rt in reversed(st.session_state.recent_tools[-5:]):
                    if st.button(f"▸ {rt}", key=f"rt_{rt}", use_container_width=True):
                        st.session_state.selected_tool = rt
                        st.session_state.show_welcome = False
                        st.rerun()
            st.divider()

        for cat, names in CATEGORIES.items():
            filtered = [n for n in names if n in TOOL_REGISTRY]
            if q:
                filtered = [n for n in filtered if q in n.lower() or q in (TOOL_REGISTRY[n].description or "").lower()]
            if fav_only:
                filtered = [n for n in filtered if n in st.session_state.favorites]
            if not filtered:
                continue
            CAT_COLORS.get(cat, "#6b7280")
            icon = CAT_ICONS.get(cat, "📦")
            with st.expander(f"{icon} {cat}", expanded=bool(q)):
                for name in filtered:
                    is_fav = name in st.session_state.favorites
                    c1, c2 = st.columns([10, 2])
                    with c1:
                        if st.button(name, key=f"sb_{name}", use_container_width=True):
                            st.session_state.selected_tool = name
                            st.session_state.show_welcome = False
                            if name in st.session_state.recent_tools:
                                st.session_state.recent_tools.remove(name)
                            st.session_state.recent_tools.append(name)
                            if len(st.session_state.recent_tools) > 10:
                                st.session_state.recent_tools.pop(0)
                            st.rerun()
                    with c2:
                        label = "⭐" if is_fav else "☆"
                        if st.button(label, key=f"fv_{name}", help="Toggle favorite"):
                            (st.session_state.favorites.discard if is_fav else st.session_state.favorites.add)(name)
                            st.rerun()
        st.divider()
        theme = st.selectbox("🎨 Theme", ["Dark", "Light"],
                            index=0 if st.session_state.theme == "dark" else 1, key="tp")
        st.session_state.theme = theme.lower()


# ── Welcome ──────────────────────────────────────────────────────────────────
def welcome():
    total = len(TOOL_REGISTRY)
    cats = len(CATEGORIES)
    hist = len(st.session_state.history)
    fav = len(st.session_state.favorites)
    used = len(st.session_state.usage_count)
    cols = st.columns(5)
    for c, (l, v, h) in zip(cols, [
        ("🔧 Total Tools", total, "81 across 13 categories"),
        ("📂 Categories", cats, "organized groups"),
        ("📜 Runs", hist, "all time"),
        ("⭐ Favorites", fav, "bookmarked"),
        ("🎯 Used", used, f"of {total} tools"),
    ]):
        with c: st.metric(l, v, h)

    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem 1rem;">
        <div style="font-size:5rem;margin-bottom:0.5rem;">⚡</div>
        <h1 style="font-size:2.8rem;background:var(--accent-gradient);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   margin-bottom:0.3rem;">Crew Tools</h1>
        <p style="font-size:1.1rem;color:var(--text-secondary);max-width:600px;margin:0 auto 1.5rem;">
            Production-ready LangChain-compatible AI tool library.<br>
            <strong>81 tools</strong> · <strong>439 tests</strong> · <strong>87% coverage</strong> · <strong>3 interfaces</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    cats_html = ""
    for cat, names in CATEGORIES.items():
        avail = sum(1 for n in names if n in TOOL_REGISTRY)
        color = CAT_COLORS.get(cat, "#6b7280")
        icon = CAT_ICONS.get(cat, "📦")
        cats_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.6rem 1rem;margin:0.2rem 0;
                    background:var(--bg-card);border:1px solid var(--border);
                    border-radius:var(--radius-sm);cursor:pointer;
                    transition:border-color 0.15s;"
             onmouseover="this.style.borderColor='{color}'"
             onmouseout="this.style.borderColor='var(--border)'">
            <span><span style="color:{color}">{icon}</span> {cat}</span>
            <span style="color:var(--text-muted);font-size:0.85rem;">{avail} tools</span>
        </div>"""
    st.markdown(f"<h3>📂 Categories</h3>{cats_html}", unsafe_allow_html=True)
    st.info("👈 Select any tool from the sidebar or type to search.")


# ── Tool Page ────────────────────────────────────────────────────────────────
def tool_page(name: str):
    tool = TOOL_REGISTRY[name]
    cat = st.session_state.get("tool_category", TOOL_TO_CATEGORY.get(name, "Uncategorized"))
    color = CAT_COLORS.get(cat, "#6b7280")
    icon = CAT_ICONS.get(cat, "📦")
    is_fav = name in st.session_state.favorites
    async_tag = " ⚡" if is_async_tool(name) else ""

    # Header
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.3rem;">
        <span style="color:{color};font-size:0.85rem;font-weight:500;">{icon} {cat}</span>
        <span style="color:var(--text-muted);">/</span>
        <span style="font-size:1rem;font-weight:600;color:var(--text-primary);">{name}{async_tag}</span>
        { '<span class="badge" style="background:var(--accent);color:white;">async</span>' if is_async_tool(name) else ''}
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([10, 1])
    with c1: st.title(f"⚡ {name}")
    with c2:
        if st.button("⭐" if is_fav else "☆", key="fb", help="Toggle favorite"):
            (st.session_state.favorites.discard if is_fav else st.session_state.favorites.add)(name)
            st.rerun()

    desc = (tool.description or "").strip()
    if desc:
        st.markdown(f"<p style='color:var(--text-secondary);font-size:1.05rem;line-height:1.6;'>{desc}</p>", unsafe_allow_html=True)

    schema = get_schema(name)
    tabs = st.tabs(["🎮 Run", "ℹ️ Info", "📜 History"])

    # ── Run ──
    with tabs[0]:
        if schema and schema.get("properties"):
            props = schema["properties"]
            required = set(schema.get("required", []))
            has_ex = name in EXAMPLES

            if has_ex and st.button("📥 Load Example Inputs", type="secondary", use_container_width=False):
                st.session_state._example = True
                for k in list(st.session_state.keys()):
                    if k.startswith(f"{name}_"): del st.session_state[k]
                st.rerun()

            with st.form(f"fm_{name}", border=False):
                st.markdown("<h3>Parameters</h3>", unsafe_allow_html=True)
                params = {}
                for fname, fs in props.items():
                    with st.container(): params[fname] = field_widget(fname, fs, name)
                cols = st.columns([1, 1, 5])
                with cols[0]: submitted = st.form_submit_button("🚀 Run", type="primary", use_container_width=True)
                with cols[1]:
                    if st.form_submit_button("🔄 Reset", use_container_width=True):
                        for k in list(st.session_state.keys()):
                            if k.startswith(f"{name}_"): del st.session_state[k]
                        st.rerun()

            st.session_state._example = False

            if submitted:
                missing = [k for k in required if params.get(k) is None or (isinstance(params.get(k), str) and not params[k].strip())]
                if missing:
                    st.error(f"Missing required: {', '.join(missing)}")
                else:
                    with st.spinner(f"Running {name}..."):
                        result, elapsed = invoke_tool(name, params)
                    st.success(f"✅ Done — {elapsed*1000:.1f}ms")
                    st.session_state.usage_count[name] += 1
                    st.session_state.history.append({"tool": name, "params": params, "result": result, "time": elapsed})
                    if len(st.session_state.history) > 200: st.session_state.history = st.session_state.history[-200:]
                    render_output(name, str(result))
        else:
            st.info("This tool has no parameters." if not schema else "All parameters are optional — click Run with defaults.")
            if st.button("🚀 Run", type="primary"):
                params = {k: v.get("default") for k, v in (schema or {}).get("properties", {}).items() if "default" in v} if schema else {}
                with st.spinner(f"Running {name}..."):
                    result, elapsed = invoke_tool(name, params)
                st.success(f"✅ Done — {elapsed*1000:.1f}ms")
                st.session_state.usage_count[name] += 1
                render_output(name, str(result))

    # ── Info ──
    with tabs[1]:
        st.markdown("""
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;">
            <table style="width:100%;border-collapse:collapse;">
        """, unsafe_allow_html=True)
        rows = [
            ("Name", f"<code>{name}</code>"),
            ("Category", f"{icon} {cat}"),
            ("Type", "⚡ Async" if is_async_tool(name) else "🔵 Sync"),
            ("Parameters", str(len(schema.get("properties", {}))) if schema else "0"),
            ("Required", str(len(schema.get("required", []))) if schema else "0"),
            ("Times Used", str(st.session_state.usage_count.get(name, 0))),
            ("Description", desc or "—"),
        ]
        for k, v in rows:
            st.markdown(f"<tr><td style='padding:0.5rem 1rem;color:var(--text-muted);'>{k}</td><td style='padding:0.5rem 1rem;'>{v}</td></tr>", unsafe_allow_html=True)
        st.markdown("</table></div>", unsafe_allow_html=True)

        if schema:
            st.markdown("<h3>Field Details</h3>", unsafe_allow_html=True)
            for fname, fs in schema.get("properties", {}).items():
                req = "🔴 Required" if fname in required else "🟢 Optional"
                dtype = fs.get("type", "any")
                fdesc = fs.get("description", "—")
                default = fs.get("default", "")
                st.markdown(f"""
                <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);
                            padding:0.6rem 1rem;margin:0.3rem 0;">
                    <strong>{fname}</strong> <span style="color:var(--text-muted);">({dtype})</span>
                    <span style="float:right;">{req}</span><br>
                    <span style="color:var(--text-secondary);font-size:0.9rem;">{fdesc}</span>
                    {f"<br><code style='font-size:0.85rem;'>default: {default}</code>" if default != "" else ""}
                </div>
                """, unsafe_allow_html=True)

    # ── History ──
    with tabs[2]:
        hist = [h for h in st.session_state.history if h["tool"] == name]
        if not hist:
            st.info("No history yet.")
        else:
            c1, c2 = st.columns([1, 5])
            with c1:
                if st.button("🗑️ Clear", type="secondary"):
                    st.session_state.history = [h for h in st.session_state.history if h["tool"] != name]
                    st.rerun()
            with c2:
                data = json.dumps(hist, indent=2, default=str)
                st.download_button("📤 Export JSON", data, f"{name}_history.json", "application/json", type="secondary")
            for i, h in enumerate(reversed(hist[-30:])):
                idx = len(hist) - i
                ms = h["time"] * 1000
                params_preview = json.dumps(h.get("params", {}), default=str)[:80]
                with st.expander(f"#{idx} · {ms:.0f}ms · {params_preview}", expanded=i == 0):
                    st.code(json.dumps(h["params"], indent=2, default=str), language="json")
                    render_output(name, h["result"])


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    init_session()
    st.markdown(CSS, unsafe_allow_html=True)
    sidebar()
    tool = st.session_state.get("selected_tool")
    if not tool or tool not in TOOL_REGISTRY or st.session_state.get("show_welcome", True):
        welcome()
    else:
        tool_page(tool)


if __name__ == "__main__":
    main()
