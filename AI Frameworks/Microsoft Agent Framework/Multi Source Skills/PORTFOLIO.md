# 🌌 Multi-Source Skill Orchestration Hub

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI: Active](https://img.shields.io/badge/FastAPI-v0.100.0+-green.svg)](https://fastapi.tiangolo.com)
[![Coverage: 79%](https://img.shields.io/badge/coverage-79%25-brightgreen.svg)](#)

A production-ready skill composition system designed for Agentic AI platforms. This framework enables autonomous AI agents to dynamically discover, validate, and execute capabilities from multiple distinct sources (File System, Python Classes, Inline Definitions) while resolving naming conflicts through deterministic priority rules and SQLite configuration persistence.

---

## 🔗 Connect & Links
- **GitHub Repository**: `github.com/username/multi-source-skills-provider`
- **LinkedIn**: `linkedin.com/in/username`
- **Portfolio Website**: `myportfolio.dev`
- **Developer Mail**: `developer@example.com`

---

## 🎯 Aim & Mission
To build a decoupled tool orchestration pipeline where AI agents do not hardcode capabilities. Instead, the agent queries a **Composed Provider** that merges tool inputs dynamically from configuration files, code directories, runtime objects, and memory. The system ensures **type safety**, **low-latency tracking**, **conflict resolution**, and **dynamic overrides**.

---

## 💡 System Rationale (What, Why, Where, How)

### ❓ WHAT is this system?
It is a dynamic tool registration and execution gateway. Rather than binding tool schemas directly into LLM agent prompts, the system provides a unified registry that aggregates tools from files (`.json`, `.yaml`, `.py`, `.md`), class methods, and inline Python decorations.

### ❓ WHY was it built?
Production multi-agent frameworks (e.g., CrewAI, AutoGen, LangGraph) must scale tools across multiple developer teams. Hardcoding tools leads to validation failures and name collisions. This project solves that by decoupling discovery from execution and enforcing strict, type-safe validation alongside configurable precedence rules.

### ❓ WHERE do components live?
- **Models**: [`models/skill.py`](file:///home/cherry/Desktop/1_Gen/Tasks/MAF/Multi%20Source%20Skills/models/skill.py) and [`models/registry.py`](file:///home/cherry/Desktop/1_Gen/Tasks/MAF/Multi%20Source%20Skills/models/registry.py) represent parameters and serialization interfaces.
- **Providers**: Core loaders (File, Inline, Class) reside in [`providers/`](file:///home/cherry/Desktop/1_Gen/Tasks/MAF/Multi%20Source%20Skills/providers/).
- **Resolver**: Normalization, overlap checks, and priority rules reside in [`resolver/`](file:///home/cherry/Desktop/1_Gen/Tasks/MAF/Multi%20Source%20Skills/resolver/).
- **Orchestration**: The cache, sqlite logger, and agent loop reside in [`agents/`](file:///home/cherry/Desktop/1_Gen/Tasks/MAF/Multi%20Source%20Skills/agents/).
- **Web App**: The FastAPI endpoints and glassmorphism HTML resides in [`app/`](file:///home/cherry/Desktop/1_Gen/Tasks/MAF/Multi%20Source%20Skills/app/).

### ❓ HOW does it work?
1. **Discover**: ComposedProvider triggers all enabled loaders on registry initialization.
2. **Normalize**: Names are stripped and reformatted to `lowercase_snake_case`.
3. **Verify**: Schemas are checked for required parameters and executable handler mappings.
4. **Resolve**: Conflicting duplicate tools are compared. Default priorities apply (`inline` > `class` > `file`) unless a runtime override exists in the SQLite table or YAML settings.
5. **Execute & Trace**: Executions are checked against the parameter JSON schema, timed, and logged persistently to SQLite.

---

## 💼 Real-World Applications

- **Enterprise AI Assistants**: Merging built-in skills with user-defined tools or local scripts dynamically.
- **Autonomous Multi-Agent Platforms**: Routing execution commands across shared tool registries with priority checks.
- **Enterprise Plugin Systems**: Dynamically loading enterprise plugins in production sandboxes.
- **AI-Powered IDE Extensions**: Resolving tool name conflicts when third-party extensions expose overlapping APIs.

---

## 🛠️ Codebase Mapping & Component Overview

```
multi-source-skills-provider/
├── agents/
│   ├── assistant.py       # Simulated LLM agent executing matched skills
│   ├── manager.py         # SkillManager caches, reloads, and aggregates configurations
│   ├── registry.py        # SkillRegistry executes callbacks and triggers type checks
│   └── db_manager.py      # SQLite database controller persisting executions & overrides
├── resolver/
│   ├── merge.py           # Pipeline normalizer, validator, and merger
│   ├── overlap_detector.py# Duplicate names scanner
│   └── priority.py        # Priority sorting engine checking manual overrides
├── providers/
│   ├── file_provider.py   # Parses JSON scripts, YAML code blocks, markdown structures, and python code
│   ├── inline_provider.py # Scans decorated functions inside python memory namespaces
│   ├── class_provider.py  # Reflects class methods decorated with @skill_method
│   └── composed_provider.py# Aggregates sub-provider lists
├── app/
│   ├── main.py            # REST API backend hosting execution and metrics controllers
│   └── static/index.html  # Glassmorphism developer console dashboard
```

---

## 📊 Database Specifications (`logs/skills_provider.db`)

We use a local SQLite instance with two performance-optimized tables:
1. **`execution_history`**: Tracks skill name, source type, arguments passed, return payloads, execution timings (`duration_ms`), status (`success`/`failed`), and error strings.
2. **`priority_overrides`**: Allows runtime settings overrides. Administrators can select a winning source type for any clashing skill, bypassing default priority rules.

---

## 📦 Local Setup & Execution Guide

### 1. Recreate Environment & Dependencies
```bash
# Recreate virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Verify Code Quality (Pytest Suite with Coverage)
To run all unit tests, database tests, and integration pipelines:
```bash
./scripts/test.sh
```
*Expectations: 14 passing tests, 0 warnings, showing 79% overall test coverage.*

### 3. Launch Development Server
To start the FastAPI web dashboard:
```bash
./scripts/run.sh
```
*Expectations: App starts on local port 8000. Accessing `http://localhost:8000` loads the dark glassmorphism dashboard.*

### 4. Run CLI Pipeline Demo
To run a command-line test of all dynamic loaders, conflict indicators, and agent execution paths:
```bash
PYTHONPATH=. ./.venv/bin/python examples/composed_provider_demo.py
```

### 5. Deploy with Docker
To compile the multi-stage Docker image and start the container:
```bash
./scripts/deploy.sh
```

---

## 🎯 Test & Coverage Expectations

Our Pytest configurations in `pyproject.toml` verify the following metrics:
- **`resolver/priority.py`**: **97% Coverage** (Verifies override routing and default priority hierarchies).
- **`resolver/merge.py`**: **91% Coverage** (Verifies snake_case formatting and metadata validation).
- **`agents/manager.py`**: **94% Coverage** (Verifies cache initialization and override merging).
- **`agents/db_manager.py`**: **82% Coverage** (Verifies SQLite tables creation, logging, overrides writing, and metrics aggregation).

---

## 🏁 Project Conclusion

The **Multi-Source Skill Orchestration Hub** establishes a robust, highly modular tool gateway for AI Agents. By leveraging SQLite metrics logging, dynamic overrides, and custom UI components, the project addresses the core pipeline challenges of tool discovery, safety validation, name collision resolution, and containerized deployment. It provides a blueprint for production-grade agentic AI software architectures.
