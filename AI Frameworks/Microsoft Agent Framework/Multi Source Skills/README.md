# 🌌 Multi-Source Skill Orchestration Hub

A production-ready skill composition system designed for agentic AI applications. This framework allows AI agents to dynamically load, normalize, validate, and execute skills from multiple independent sources (File System, Python Classes, Inline Definitions) while managing name collisions using a priority resolution engine.

---

## 🎯 Project Vision & Architecture

In production AI platforms (like Anthropic Tools, LangGraph, CrewAI, AutoGen, or internal enterprise agent engines), tools are rarely hardcoded in a single script. They are compiled dynamically from various repositories, plugins, and local configurations. This project implements that orchestrating architecture.

### The Composition Pipeline:

```
  File System Skills       Inline Function Skills       Class Module Skills
 (JSON, YAML, PY, MD)      (@register_inline_skill)      (@skill_method)
          │                           │                         │
          └───────────────────────────┼─────────────────────────┘
                                      ▼
                             Composed Provider
                                      │
                                      ▼
                         Normalization & Validation
                        (snake_case & metadata check)
                                      │
                                      ▼
                              Conflict Resolver
                      (Priorities & priorities.yaml Overrides)
                                      │
                                      ▼
                             Unified Skill Registry
                                      │
                                      ▼
                        AI Assistant / REST Endpoint
```

---

## 🛠️ Tech Stack & Requirements

- **Backend**: Python 3.8+ (tested on Python 3.14), FastAPI, Uvicorn, Pydantic v2, PyYAML.
- **Frontend**: Single Page Dashboard (HTML5, Vanilla CSS Glassmorphism, Vanilla ES6 Javascript, Google Font Outfit).
- **Testing**: Pytest.
- **OS**: Linux / MacOS / Windows. Fully compatible with lightweight systems (no GPU or external LLM API keys required).

---

## 📂 Professional Folder Structure

```
multi-source-skills-provider/
├── agents/                  # Skill registry, caching managers, and AI agent traces
│   ├── assistant.py         # Mock reasoning loops (Thought->Action->Observation)
│   ├── manager.py           # SkillManager coordinates reloading and caches registry
│   └── registry.py          # SkillRegistry maps parameters and executes handlers
├── app/                     # FastAPI backend and UI static assets
│   ├── main.py              # REST API endpoints and static route mounts
│   └── static/
│       └── index.html       # Rich glassmorphism dashboard UI
├── configs/                 # Config files for providers and priority rules
│   ├── priorities.yaml      # Global defaults and specific skill source overrides
│   ├── providers.yaml       # Path configurations and allowed extensions
│   └── settings.py          # Configuration loading with safe fallbacks
├── docs/                    # Detailed system design markdown documentation
├── examples/                # Runnable script examples demonstrating providers
│   ├── class_provider_demo.py
│   ├── file_provider_demo.py
│   └── composed_provider_demo.py
├── models/                  # Base type schemas (Pydantic v2)
│   ├── provider.py          # Provider metadata
│   ├── registry.py          # Registry summary & conflict detail schemas
│   └── skill.py             # Skill parameters and execution wrappers
├── providers/               # Abstract base classes and source-specific loading
│   ├── base_provider.py
│   ├── class_provider.py
│   ├── file_provider.py
│   ├── inline_provider.py
│   └── composed_provider.py
├── resolver/                # Merge pipeline logic
│   ├── merge.py             # Normalization, verification, and composition
│   ├── overlap_detector.py  # Groups matching tool names
│   └── priority.py          # Selects winning candidates
├── skills/                  # Core skill source directories
│   ├── classes/             # Class modules (@skill_method decorated)
│   ├── file/                # JSON, YAML, PY, and MD skill source files
│   ├── inline/              # Python inline scripts
│   └── shared/              # Common utilities
├── tests/                   # Pytest test files
│   ├── test_pipeline.py
│   ├── test_providers.py
│   └── test_resolver.py
├── scripts/                 # Executable automation shell scripts
│   ├── run.sh               # Runs uvicorn dashboard development server
│   └── test.sh              # Runs the pytest suite
├── pyproject.toml           # Pytest & project configurations
└── requirements.txt         # Core dependencies
```

---

## 🚀 Getting Started

### 1. Installation
Clone this repository and set up a virtual environment:
```bash
# Recreate virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Tests
We maintain **100% passing unit and integration tests** verifying validation, caching, merging, and reasoning loops:
```bash
# Execute pytest via helper script
./scripts/test.sh

# Or run pytest directly
PYTHONPATH=. pytest
```

### 3. Launching the Hub Dashboard
Start the development server and open the browser interface:
```bash
# Start server
./scripts/run.sh
```
Now, navigate to **`http://localhost:8000`** in your browser.

---

## 🕹️ Interactive Features of the Dashboard

- **Sync Sources**: Triggers hot reloading across the file system, inline code, and classes dynamically.
- **Visual Pipeline Flow**: Tracks the data journey from providers through normalization, verification, and conflict checks.
- **Unified Skill Directory**: Search, filter, and review parameters, source types, and priorities for all merged skills.
- **Conflict Override Diagnostics**: View clashing tools, individual priorities, the winning source, and the detailed resolution logs.
- **Interactive Skill Console**: Click any registered skill, fill out the autogenerated form parameters, invoke the tool, and inspect the response.
- **AI Agent Chat Console**: Type natural language commands and observe the agent's Thought -> Action -> Observation reasoning loop.

---

## 🛠️ Adding Custom Skills

### Inline Skills (`skills/inline/sample_inline.py`)
```python
from providers.inline_provider import register_inline_skill

@register_inline_skill(
    name="my_inline_tool",
    description="Explain inline details",
    parameters={"arg1": {"type": "string"}}
)
def run_tool(arg1: str):
    return f"Inline: {arg1}"
```

### Class Skills (`skills/classes/sample_class.py`)
```python
from providers.class_provider import skill_method

class DatabaseTools:
    @skill_method(name="db_status", description="Get db status")
    def status(self) -> str:
        return "Connected"
```

### File Skills (`skills/file/my_tool.yaml`)
```yaml
name: "yaml_tool"
description: "Executes custom python code"
version: "1.0.0"
parameters:
  message:
    type: "string"
execute_code: |
  def execute(message):
      return f"Code: {message}"
```
