<div align="center">
  <br>
  <img src="https://img.shields.io/badge/version-0.1.0-4f46e5?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/tests-439-10b981?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-86.9%25-22c55e?style=for-the-badge" alt="Coverage">
  <img src="https://img.shields.io/badge/tools-81-8b5cf6?style=for-the-badge" alt="Tools">
  <img src="https://img.shields.io/badge/license-MIT-f59e0b?style=for-the-badge" alt="License">
  <br><br>
  <h1>⚡ Crew Tools</h1>
  <p><strong>Production-ready LangChain-compatible AI tool library</strong></p>
  <p>81 tools · 439 tests · 87% coverage · 0 warnings · 3 interfaces</p>
  <br>
</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Tool Categories](#-tool-categories)
- [Interfaces](#-interfaces)
  - [Streamlit UI](#-streamlit-ui)
  - [CLI](#-cli)
  - [FastAPI Server](#-fastapi-server)
- [Installation](#-installation)
- [All 81 Tools](#-all-81-tools)
- [Development](#-development)
- [Docker](#-docker)
- [CI/CD](#-cicd)
- [Plugin System](#-plugin-system)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [FAQ](#-faq)
- [License](#-license)

---

## 🎯 Overview

**Crew Tools** is a comprehensive, production-ready library of **81 LangChain-compatible AI tools** with **3 interfaces** (CLI, REST API, Streamlit UI), **439 tests**, **87% coverage**, and professional infrastructure (Docker, CI/CD, logging, config, plugins).

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔧 **81 Tools** | 13 categories — text, math, conversion, validation, web, files, data, code, crypto, templates, charts, system, memory |
| 🖥️ **3 Interfaces** | Streamlit UI, CLI, FastAPI REST API |
| 🧪 **439 Tests** | Unit + property-based + fuzz, 86.9% coverage |
| 🐳 **Dockerized** | Ready-to-deploy container |
| 🔌 **Plugin System** | `entry_points`-based extensibility |
| 📝 **Logging** | Structured JSON, context vars, rotating files |
| ⚙️ **Configuration** | YAML + environment variables |
| 🎨 **Extras** | `[dev]` `[api]` `[web]` `[data]` `[code]` `[templates]` `[charts]` `[ui]` |
| 🔒 **Safe & Secure** | Input validation, sandboxed code execution, rate limiting |
| ⚡ **Async Support** | Async tools + batch processing |
| ✅ **100% Tool Tested** | All 81 tools verified with example inputs — 0 runtime errors |

### 🎯 Use Cases

| Domain | Tools | Example |
|--------|-------|---------|
| **AI/LLM Agents** | All 81 tools | Give your agent word counting, web search, calculation, data analysis |
| **Data Processing** | read/write, csv/json, describe, filter, sort, aggregate | ETL pipelines without Pandas dependency |
| **Web Scraping** | web_fetch, web_search, rss_parse, dns_lookup, port_check, http_status | Gather and analyze web data |
| **DevOps** | system_info, which_program, env_get, run_python, format_code | Automate system tasks |
| **Content Creation** | word_counter, text_stats, reading_time, diff_text, render_template, markdown_table, html_table | Writing and reporting pipelines |
| **Security** | validate_email, validate_url, validate_phone, hash_string, base64, random_password | Input validation and crypto |
| **Data Viz** | create_bar/line/pie/histogram charts | Inline chart generation (base64 PNG) |
| **Conversions** | convert, timezone_convert, format_date, parse_date, json/yaml/toml/xml | Universal format conversion |

---

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/anomalyco/crew-tools.git
cd crew-tools
pip install -e ".[ui]"  # with Streamlit UI

# 2. Launch Streamlit UI
crew-tools streamlit
# → opens http://localhost:8501

# 3. Or use CLI
crew-tools list
crew-tools info web_search
crew-tools --help

# 4. Or serve API
pip install -e ".[api]"
crew-tools serve
# → http://localhost:8000/docs
```

---

## 🏗 Architecture

```
                   ┌──────────────────────┐
                   │     Streamlit UI      │  port 8501
                   │  (crew_tools/ui/)     │
                   └──────────┬───────────┘
                              │
┌──────────┐     ┌───────────┴───────────┐     ┌──────────┐
│   CLI    │────▶│    TOOL_REGISTRY      │◀────│  FastAPI │
│ argparse │     │  81 tools / 29 mods   │     │  /tools  │
└──────────┘     └───────────┬───────────┘     └──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   ┌──────────┐      ┌──────────────┐      ┌──────────────┐
   │ Plugins  │      │  Production  │      │  Extras      │
   │entry_pts │      │RateLimiter   │      │[web][data]   │
   └──────────┘      │Cache/Retry   │      │[code][charts]│
                     │Batch/Async   │      └──────────────┘
                     └──────────────┘
```

---

## 📂 Tool Categories

| Category | Icon | Tools | Color |
|----------|------|-------|-------|
| Text & Language | 📝 | 10 | `#3b82f6` |
| Math & Stats | 🔢 | 10 | `#10b981` |
| Conversion | 📐 | 9 | `#f59e0b` |
| Validation | ✅ | 5 | `#8b5cf6` |
| Web & Network | 🌐 | 6 | `#06b6d4` |
| File & Data | 📁 | 9 | `#14b8a6` |
| Code | 💻 | 2 | `#f97316` |
| Crypto & Encoding | 🔐 | 4 | `#ef4444` |
| Templates & Format | 📄 | 12 | `#ec4899` |
| Charts | 📊 | 4 | `#a855f7` |
| System | ⚙️ | 4 | `#6b7280` |
| Memory | 🧠 | 4 | `#84cc16` |
| Async | ⚡ | 3 | `#6366f1` |

---

## 🖥️ Interfaces

### 🎨 Streamlit UI

The flagship interface — a beautiful, interactive web dashboard.

```
crew-tools streamlit
# or: streamlit run crew_tools/ui/streamlit_app.py
```

**Features:**
- **13 tool categories** in sidebar with color coding
- **🔍 Search** — real-time filtering by name and description
- **⭐ Favorites** — bookmark tools for quick access
- **🕐 Recent** — last 10 tools used
- **📥 Load Example** — pre-fill inputs with realistic examples
- **Dynamic forms** — auto-generated from Pydantic schemas (text, textarea, select, number, slider, checkbox)
- **3-pane output** — Preview / Raw / Debug for every result
- **Chart rendering** — inline PNG charts from chart tools
- **Async tool support** — seamless `.ainvoke()` for async tools via `asyncio.run()`
- **Run history** — per-tool history, export to JSON
- **Copy to clipboard** — one-click on any output
- **Dark/Light theme** — toggle in sidebar
- **Usage stats** — per-tool execution count

### 🖥️ CLI

```bash
crew-tools list                    # List all tools
crew-tools info web_search         # Tool details + schema
crew-tools version                 # Show version
crew-tools config                  # Show current config
crew-tools plugins                 # Show plugins
crew-tools serve --port 8000       # Start API server
crew-tools streamlit               # Start Streamlit UI
```

### 🌐 FastAPI Server

```bash
crew-tools serve
# GET  /health           → {"status": "ok"}
# GET  /tools            → list all tools
# POST /tools/{name}/invoke → run a tool
```

Example:
```bash
curl -X POST http://localhost:8000/tools/word_counter_v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

---

## 📦 Installation

### Basic
```bash
pip install crew-tools
```

### With extras
```bash
# Streamlit UI
pip install "crew-tools[ui]"

# API server
pip install "crew-tools[api]"

# Web tools (search, fetch, RSS)
pip install "crew-tools[web]"

# Data tools (pandas-based)
pip install "crew-tools[data]"

# Code tools (format, run)
pip install "crew-tools[code]"

# Templates (Jinja2)
pip install "crew-tools[templates]"

# Charts (matplotlib)
pip install "crew-tools[charts]"

# Development
pip install "crew-tools[dev]"

# Everything
pip install "crew-tools[api,web,data,code,templates,charts,ui,dev]"
```

### From source
```bash
git clone https://github.com/anomalyco/crew-tools.git
cd crew-tools
pip install -e ".[dev,api,web,data,code,templates,charts,ui]"
```

---

## 🔧 All 81 Tools

<details>
<summary><b>📝 Text & Language</b> (10)</summary>

| Tool | Description |
|------|-------------|
| `word_counter_v1` | Count words in text |
| `word_counter_v2` | Count words with parameter validation |
| `word_counter_v3` | Count words with Pydantic schema |
| `word_counter_v4` | Advanced word counting with filtering options |
| `word_counter_safe` | Word counting with input validation |
| `word_counter_advanced` | Word counting with validation + safe error handling |
| `text_stats` | Comprehensive text statistics (words, chars, sentences, readability) |
| `count_sentences` | Count sentences in text |
| `reading_time` | Estimate reading time |
| `diff_text` | Generate unified diff between two texts |

</details>

<details>
<summary><b>🔢 Math & Stats</b> (10)</summary>

| Tool | Description |
|------|-------------|
| `calculate_v1` | Evaluate math expression string |
| `calculate_v2` | Basic arithmetic (2 numbers + operator) |
| `calculate_v3` | Arithmetic with Pydantic schema |
| `calculate_v4` | Validated arithmetic with enum operators |
| `calculate_v5` | Math expression with safety & precision |
| `calculate_safe` | Full input validation arithmetic |
| `basic_stats` | Mean, median, mode, stdev, variance, min, max, range |
| `percentile` | Compute arbitrary percentiles |
| `moving_average` | Compute moving averages |
| `outliers` | Detect outliers via IQR or z-score |

</details>

<details>
<summary><b>📐 Conversion</b> (9)</summary>

| Tool | Description |
|------|-------------|
| `convert_v1` | Basic unit conversion |
| `convert_v2` | Unit conversion with validation |
| `convert_v3` | Unit conversion with Pydantic |
| `convert_v4` | Fully validated unit conversion |
| `convert_safe` | Unit conversion with full input validation |
| `timezone_convert` | Convert datetime between timezones |
| `format_date` | Parse and reformat date strings |
| `parse_date` | Parse natural language dates |
| `current_time` | Get current time in any timezone |

</details>

<details>
<summary><b>✅ Validation</b> (5)</summary>

| Tool | Description |
|------|-------------|
| `validate_email` | Validate email addresses |
| `validate_url` | Validate URLs (http, https, ftp) |
| `validate_phone` | Validate phone numbers |
| `validate_v2` | Validate against multiple formats |
| `validate_json` | Validate JSON strings |

</details>

<details>
<summary><b>🌐 Web & Network</b> (6)</summary>

| Tool | Description |
|------|-------------|
| `web_fetch` | Fetch URL → markdown text |
| `web_search` | Search web via DuckDuckGo |
| `rss_parse` | Parse RSS/Atom feeds |
| `dns_lookup` | DNS record lookup (A, AAAA, MX, etc.) |
| `port_check` | Check TCP port status |
| `http_status` | Check HTTP status + headers |

</details>

<details>
<summary><b>📁 File & Data</b> (9)</summary>

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write content to file (auto-creates dirs) |
| `list_dir` | List directory contents |
| `csv_to_json` | Convert CSV → JSON |
| `json_to_csv` | Convert JSON → CSV |
| `describe_data` | CSV column statistics (pandas) |
| `filter_rows` | Filter CSV rows by condition |
| `sort_rows` | Sort CSV rows by column |
| `aggregate_data` | Group and aggregate CSV data |

</details>

<details>
<summary><b>💻 Code</b> (2)</summary>

| Tool | Description |
|------|-------------|
| `run_python` | Execute Python code in sandboxed subprocess |
| `format_code` | Format Python code with ruff |

</details>

<details>
<summary><b>🔐 Crypto & Encoding</b> (4)</summary>

| Tool | Description |
|------|-------------|
| `hash_string` | Hash with md5/sha1/sha256/sha512 |
| `base64_encode` | Encode to base64 |
| `base64_decode` | Decode from base64 |
| `random_password` | Cryptographically secure password generator |

</details>

<details>
<summary><b>📄 Templates & Format</b> (12)</summary>

| Tool | Description |
|------|-------------|
| `render_template` | Render Jinja2 templates |
| `regex_search` | Search with regex patterns |
| `regex_replace` | Replace with regex patterns |
| `json_prettify` | Format/prettify JSON |
| `yaml_parse` | Parse YAML → JSON |
| `yaml_dump` | Convert JSON → YAML |
| `toml_parse` | Parse TOML → JSON |
| `xml_parse` | Parse XML → JSON-like structure |
| `markdown_table` | Create Markdown tables |
| `html_table` | Create HTML tables |
| `word_wrap` | Wrap text to line width |

</details>

<details>
<summary><b>📊 Charts</b> (4)</summary>

| Tool | Description |
|------|-------------|
| `create_bar_chart` | Bar chart → base64 PNG |
| `create_line_chart` | Line chart → base64 PNG |
| `create_pie_chart` | Pie chart → base64 PNG |
| `create_histogram` | Histogram → base64 PNG |

</details>

<details>
<summary><b>⚙️ System</b> (4)</summary>

| Tool | Description |
|------|-------------|
| `system_info` | OS, CPU, memory, Python version |
| `os_info` | Operating system details |
| `which_program` | Locate program on PATH |
| `env_get` | Get environment variable value |

</details>

<details>
<summary><b>🧠 Memory</b> (4)</summary>

| Tool | Description |
|------|-------------|
| `session_set` | Store value in session |
| `session_get` | Retrieve value from session |
| `session_list` | List all session keys |
| `session_clear` | Clear all session values |

</details>

<details>
<summary><b>⚡ Async</b> (3)</summary>

| Tool | Description |
|------|-------------|
| `async_calculate` | Asynchronous arithmetic |
| `async_convert` | Asynchronous unit conversion |
| `async_word_counter` | Asynchronous word counting |

</details>

---

## 🛠 Development

```bash
# Setup
git clone https://github.com/anomalyco/crew-tools.git
cd crew-tools
pip install -e ".[dev]"

# Run tests
pytest tests/
pytest tests/ --cov=crew_tools

# Lint
ruff check crew_tools/ tests/

# Lint + fix
ruff check crew_tools/ tests/ --fix

# Pre-commit
pre-commit install
pre-commit run --all-files

# Build
python -m build
```

---

## 🐳 Docker

```bash
# Build
docker build -t crew-tools .

# Run Streamlit UI
docker run -p 8501:8501 crew-tools streamlit

# Run API server
docker run -p 8000:8000 crew-tools serve
```

---

## 🔄 CI/CD

GitHub Actions automatically runs on every push and PR:
- **Matrix**: Python 3.10 / 3.11 / 3.12
- **Steps**: ruff lint → pytest with coverage → Codecov upload
- **Coverage gate**: 85% minimum

---

## 🔌 Plugin System

Extend with custom tools via `importlib.metadata` entry points:

```python
# my_plugin.py
from crew_tools._plugins import ToolPlugin
from langchain_core.tools import tool

my_tools = {
    "my_custom_tool": tool(lambda x: f"Hello {x}")(lambda x: x)
}

class MyPlugin(ToolPlugin):
    name = "my_plugin"
    description = "My custom tools"
    tools = my_tools
```

```toml
# pyproject.toml
[project.entry-points."crew_tools.plugins"]
my_plugin = "my_plugin:MyPlugin"
```

---

## ⚙️ Configuration

`config.yaml` (auto-discovered in working directory):

```yaml
log:
  level: INFO
  json_output: true
  file: null

cache:
  default_ttl: 300.0
  maxsize: 128

rate_limit:
  default_calls_per_second: 10.0

server:
  host: 127.0.0.1
  port: 8000
  reload: false
```

Override with `CREW_*` environment variables (e.g. `CREW_SERVER_PORT=9000`).

---

## 📁 Project Structure

```
crew-tools/
├── crew_tools/                  # Main package
│   ├── __init__.py              # Registry of all 81 tools
│   ├── _version.py              # v0.1.0
│   ├── cli.py                   # 7 CLI subcommands
│   ├── api_server.py            # FastAPI (3 endpoints)
│   ├── _config.py               # YAML + env config loader
│   ├── _logging.py              # Structured JSON logger
│   ├── _plugins.py              # Plugin discovery system
│   ├── production.py            # RateLimiter, Cache, Retry, Batch
│   ├── async_tools.py           # 3 async tools
│   ├── validation.py            # Validation utilities
│   ├── calculator.py            # calculate_v1–v5, calculate_safe
│   ├── unit_converter.py        # convert_v1–v4, convert_safe
│   ├── word_counter.py          # word_counter_v1–v4
│   ├── validator.py             # Email/URL/phone validation
│   ├── text_tools.py            # Text stats, sentences, reading time
│   ├── safe_converter.py        # Safe conversion wrappers
│   ├── safe_word_counter.py     # Safe word count wrappers
│   ├── web_tools.py             # Fetch, search, RSS
│   ├── file_tools.py            # Read/write/list/csv/json
│   ├── data_tools.py            # Pandas-based data tools
│   ├── code_tools.py            # Run Python, format code
│   ├── template_tools.py        # Jinja2, regex, diff
│   ├── time_tools.py            # Date/time/timezone tools
│   ├── crypto_tools.py          # Hash, base64, passwords
│   ├── system_tools.py          # System info, which, env
│   ├── memory_tools.py          # Session memory
│   ├── chart_tools.py           # Matplotlib charts
│   ├── format_tools.py          # YAML/TOML/XML/JSON
│   ├── network_tools.py         # DNS/port/HTTP
│   ├── stats_tools.py           # Statistics tools
│   ├── report_tools.py          # Markdown/HTML tables, word wrap
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py     # Streamlit interface
├── tests/                       # 439 tests across 25 files
│   ├── conftest.py
│   ├── test_*.py
│   └── ...
├── pyproject.toml               # Build + config
├── config.yaml                  # Default config
├── Dockerfile                   # Container
├── Makefile                     # Dev commands
├── .pre-commit-config.yaml
├── .editorconfig
├── .github/workflows/test.yml   # CI/CD
└── README.md
```

---

## ❓ FAQ

**Q: Is this free?**  
A: Yes! MIT license — free to use, modify, and distribute.

**Q: Does it require LangChain?**  
A: It's LangChain-compatible but all tools work independently. Only `langchain-core` is needed for the `@tool` decorator.

**Q: Can I use it without LangChain?**  
A: Yes. Import tools directly from their modules and call them as regular functions.

**Q: What Python versions are supported?**  
A: Python 3.10, 3.11, 3.12.

**Q: Does it require internet?**  
A: Only for web/network tools (`web_fetch`, `web_search`, `rss_parse`, `dns_lookup`, `port_check`, `http_status`). All other tools work fully offline.

**Q: Can I add my own tools?**  
A: Yes! Either contribute to the library or use the plugin system to add custom tools.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p>Built with ⚡ using Python, LangChain, Streamlit, and ❤️</p>
  <p>
    <a href="https://github.com/anomalyco/crew-tools">GitHub</a> ·
    <a href="https://pypi.org/project/crew-tools/">PyPI</a> ·
    <a href="https://github.com/anomalyco/crew-tools/issues">Issues</a>
  </p>
</div>
