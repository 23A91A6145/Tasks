# 🛡️ DeepRepo Reviewer — Autonomous AI Codebase Review Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![Pydantic AI](https://img.shields.io/badge/Pydantic--AI-v2.30-orange.svg)](https://ai.pydantic.dev/)
[![Pydantic Deep](https://img.shields.io/badge/Pydantic--Deep-v0.3.43-purple.svg)](https://github.com/pydantic/pydantic-deep)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Protocol%20Ready-blueviolet.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-48%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **DeepRepo Reviewer (P13 Deep Agent)** is an autonomous multi-agent software-engineering review and DevSecOps platform. Built on **Pydantic Deep** and **Pydantic AI**, it inspects Git repositories, plans multi-step review workflows, dispatches 5 domain-specialist sub-agents in parallel, verifies citations against real code, learns project architectural memory, and exposes a FastAPI REST API, interactive Web Dashboard, and Model Context Protocol (MCP) server.

---

## 🌟 Key Capabilities & Features

- 🧠 **Autonomous 7-Step Planning Engine**: Profiles languages, frameworks, entrypoints, and Git diffs to compile prioritized execution steps.
- 🔒 **Sandboxed Filesystem Security**: Boundary isolation prevents path traversal attacks (`../../`) and blocks access to sensitive credentials (`.env`, `.pem`, secrets).
- 🌿 **Native Git Intelligence**: Extracts branches, commits, staging changes, and file diffs using `GitPython`.
- 🤖 **5 Domain-Specialized Sub-Agents**:
  - **Security Reviewer (`SecurityReviewer`)**: SQL injection, credential leaks, command injection (`shell=True`), insecure deserialization, `eval`/`exec`, SSL bypass, permissive CORS.
  - **Bug & Logic Reviewer (`BugReviewer`)**: Mutable default arguments, bare `except:` statements, string literal identity checks (`is`), unmanaged file resources, in-place sort comparisons.
  - **Architecture Reviewer (`ArchitectureReviewer`)**: Monolithic files, global mutable state, deprecated library imports, cyclomatic nesting.
  - **Performance Reviewer (`PerformanceReviewer`)**: N+1 database queries, blocking synchronous calls (`time.sleep`, `requests`) in async def routines, string concatenation loops.
  - **Test Reviewer (`TestReviewer`)**: Missing assertions, empty stub tests, dummy assertions (`assert True`), untested changesets.
- 🎯 **Verification Sub-Agent (`VerificationAgent`)**: Validates code evidence and line numbers against the real filesystem to eliminate false positives and calculate precision rates.
- 🧠 **Persistent Project Memory (`ProjectMemory`)**: Stores architectural rules, intentional exceptions, and false-positive suppressions across review runs in `.deeprepo/memory.json`.
- 💾 **Fault-Tolerant Checkpoints (`ReviewCheckpointManager`)**: Saves snapshot state after each phase to enable instant recovery.
- 🔌 **Model Context Protocol (MCP) Server**: First-class MCP tools (`deeprepo_inspect`, `deeprepo_plan`, `deeprepo_review`) for Claude Desktop, Cursor, Antigravity, and OpenCode.
- 🐙 **GitHub PR Automation**: Evaluates PR pass/fail policy, formats Markdown review comments, and builds GitHub Check Run annotations.
- 🌐 **FastAPI REST API & Interactive Web Dashboard**: Single-page web UI for triggering reviews, visualizing pipelines, filtering findings, and inspecting reports.
- 📊 **Triple Report Exporters**: Generates GitHub-flavored Markdown (`reports/*.md`), structured JSON (`reports/*.json`), and responsive HTML reports (`reports/*.html`).
- 📈 **Evaluation & Benchmark Harness**: Built-in ground-truth evaluation harness measuring precision, recall, and F1 scores (`deeprepo evaluate`).
- ⚡ **Auto-Confirm Mode**: Non-blocking execution mode (`--auto-confirm` / `-y`) for seamless CI/CD automation.

---

## 📐 Multi-Agent Topology & Pipeline

```
                      Target Git Repository
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Workspace Manager  │ (Safe boundary, profiling)
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Git Inspector    │ (Diff extraction, commit stats)
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Autonomous Planner  │ (7-step dynamic review plan)
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Review Coordinator  │ (Parallel Async Dispatcher)
                    └──────────┬──────────┘
                               │
          ┌────────────┬───────┴───────┬────────────┬────────────┐
          ▼            ▼               ▼            ▼            ▼
     [Security]     [Bugs]      [Architecture] [Performance] [Testing]
     Reviewer      Reviewer        Reviewer      Reviewer     Reviewer
          │            │               │            │            │
          └────────────┴───────┬───────┴────────────┴────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Verification Agent  │ (Evidence check & False-Positive filter)
                    └──────────┬──────────┘
                               │
                    ┌─────────────────────┐
                    │ Project Memory & CP │ (Persistent Context & Checkpoints)
                    └──────────┬──────────┘
                               │
                    ┌─────────────────────┐
                    │ Finding Aggregator  │ (Deduplication, severity rank)
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
      Markdown (.md)      JSON (.json)       HTML (.html)
            │                  │                  │
            └──────────────────┼──────────────────┘
                               ▼
               ┌───────────────────────────────┐
               │ FastAPI API & Web Dashboard   │
               │ MCP Server & GitHub PR Review │
               └───────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Installation
Using `uv` (recommended):
```bash
# Create virtual environment and install dependencies
uv pip install -e ".[dev]"
```

### 2. Environment Setup
Configure your LLM provider in `.env` (Google Gemini Pro / Flash recommended):
```bash
cp .env.example .env
# Set your GEMINI_API_KEY in .env
```

### 3. Verify Environment & Multi-Agent Diagnostics
```bash
.venv/bin/python -m app.cli test-env
```

---

## 💻 CLI Commands & Usage

### 1. Launch FastAPI Server & Interactive Web Dashboard
```bash
.venv/bin/python -m app.cli serve --port 8000
```
- **Web Dashboard UI:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Execute Multi-Agent Autonomous Review
```bash
# Review current repository with all 5 specialist sub-agents
.venv/bin/python -m app.cli review . --auto-confirm

# Target specific specialist sub-agents (e.g. security and performance only)
.venv/bin/python -m app.cli review fixtures/vulnerable -s security,performance --auto-confirm
```

### 3. Run Ground-Truth DevSecOps Benchmark
```bash
.venv/bin/python -m app.cli evaluate
```

### 4. Start Model Context Protocol (MCP) Server
```bash
.venv/bin/python -m app.cli mcp
```

### 5. Inspect Persistent Project Memory
```bash
.venv/bin/python -m app.cli memory fixtures/vulnerable
```

### 6. Inspect Repository Structure & Git Metadata
```bash
.venv/bin/python -m app.cli inspect .
```

### 7. Generate 7-Step Multi-Agent Plan
```bash
.venv/bin/python -m app.cli plan fixtures/vulnerable
```

---

## 🌐 FastAPI REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | System health check, active specialists, and LLM status |
| `POST` | `/api/v1/inspect` | Profile repository language, frameworks, and Git metadata |
| `POST` | `/api/v1/plan` | Generate autonomous review execution plan |
| `POST` | `/api/v1/review` | Execute multi-agent review pipeline and return findings |
| `GET` | `/api/v1/reports` | List all saved review report runs |
| `GET` | `/api/v1/reports/{run_id}/html` | Render standalone responsive HTML report |
| `GET` | `/api/v1/reports/{run_id}/markdown` | Fetch raw Markdown report text |
| `GET` | `/` | Web Dashboard Single Page Application |

---

## 🔌 MCP (Model Context Protocol) Client Configuration

To connect DeepRepo Reviewer to **Claude Desktop**, **Cursor**, **Antigravity**, or **OpenCode**, add the following to your `mcp.json` / `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "deeprepo": {
      "command": "/home/cherry/Desktop/1_Gen/Tasks/Pydantic/Codebase Review/.venv/bin/python",
      "args": ["-m", "app.cli", "mcp", "/home/cherry/Desktop/1_Gen/Tasks/Pydantic/Codebase Review"]
    }
  }
}
```

---

## 🧪 Comprehensive Test Suite (48 Tests Passed)

Run the full pytest suite:
```bash
.venv/bin/pytest -v
```

```text
============================= test session starts ==============================
collected 48 items

tests/agent/test_deep_agent.py::test_reviewer_initialization_and_run PASSED
tests/evaluation/test_benchmark.py::test_evaluation_benchmark_execution PASSED
tests/integration/test_full_platform_v5.py::test_full_v5_platform_end_to_end PASSED
tests/integration/test_full_v1_pipeline.py::test_v1_pipeline_on_vulnerable_fixture PASSED
tests/integration/test_full_v1_pipeline.py::test_v1_pipeline_on_clean_fixture PASSED
tests/integration/test_v3_multi_agent.py::test_full_v3_multi_agent_pipeline_on_fixtures PASSED
tests/integration/test_v3_multi_agent.py::test_v3_specialist_filtering PASSED
tests/integration/test_v4_pipeline.py::test_full_v4_pipeline_with_verification PASSED
tests/integration/test_v4_pipeline.py::test_v4_fastapi_review_and_html_generation PASSED
tests/reviewers/test_architecture.py::test_architecture_reviewer_detects_global_state_and_deprecated_imports PASSED
tests/reviewers/test_bugs.py::test_bug_reviewer_detects_mutable_defaults_and_bare_except PASSED
tests/reviewers/test_performance.py::test_performance_reviewer_detects_blocking_async_and_n_plus_one PASSED
tests/reviewers/test_security.py::test_security_reviewer_detects_sqli_and_secrets PASSED
tests/reviewers/test_testing.py::test_test_reviewer_detects_empty_tests_and_missing_assertions PASSED
tests/unit/test_api.py::test_api_health_check PASSED
tests/unit/test_api.py::test_api_inspect_endpoint PASSED
tests/unit/test_api.py::test_api_plan_endpoint PASSED
tests/unit/test_api.py::test_api_review_endpoint PASSED
tests/unit/test_api.py::test_api_reports_list_and_dashboard_root PASSED
tests/unit/test_cli.py::test_cli_test_env PASSED
tests/unit/test_cli.py::test_cli_inspect PASSED
tests/unit/test_cli.py::test_cli_plan PASSED
tests/unit/test_cli.py::test_cli_review PASSED
tests/unit/test_coordinator.py::test_coordinator_parallel_dispatch_and_deduplication PASSED
tests/unit/test_filesystem.py::test_workspace_safe_reading PASSED
tests/unit/test_filesystem.py::test_workspace_path_traversal_blocked PASSED
tests/unit/test_filesystem.py::test_workspace_blocked_file_patterns PASSED
tests/unit/test_filesystem.py::test_workspace_grep_search PASSED
tests/unit/test_git.py::test_git_inspector_non_git_directory PASSED
tests/unit/test_git.py::test_git_inspector_live_repo PASSED
tests/unit/test_github.py::test_github_pr_verdict_evaluation PASSED
tests/unit/test_github.py::test_github_pr_comment_formatting PASSED
tests/unit/test_github.py::test_github_check_annotations PASSED
tests/unit/test_mcp.py::test_mcp_server_lists_tools PASSED
tests/unit/test_mcp.py::test_mcp_server_call_inspect_and_plan PASSED
tests/unit/test_memory_checkpoints.py::test_project_memory_save_and_load PASSED
tests/unit/test_memory_checkpoints.py::test_checkpoint_manager_save_and_load PASSED
tests/unit/test_planner.py::test_review_planner_creates_structured_steps PASSED
tests/unit/test_reports.py::test_markdown_report_generation PASSED
tests/unit/test_reports.py::test_json_report_generation PASSED
tests/unit/test_reports.py::test_html_report_generation PASSED
tests/unit/test_schemas.py::test_finding_schema_validation PASSED
tests/unit/test_review_plan_schema PASSED
tests/unit/test_repo_metadata_schema PASSED
tests/unit/test_verifier.py::test_verifier_confirms_valid_line_and_evidence PASSED
tests/unit/test_verifier.py::test_verifier_rejects_out_of_bounds_lines PASSED
tests/unit/test_verifier.py::test_verifier_rejects_suppressed_lines PASSED
tests/unit/test_verifier.py::test_verifier_verify_all_calculates_precision PASSED

======================== 48 passed in 2.23s ========================
```

---

## 🗂️ Production Repository Structure

```
deeprepo-reviewer/
├── app/
│   ├── agent/               # Deep Agent implementation & dependency container
│   ├── api/                 # FastAPI REST API routes & app factory
│   ├── config/              # Pydantic Settings & environment config
│   ├── evaluation/          # Ground-truth precision & regression benchmark harness
│   ├── git/                 # Git intelligence & diff parsing engine
│   ├── github/              # GitHub PR Webhook parser & comment generator
│   ├── mcp/                 # Model Context Protocol (MCP) server implementation
│   ├── orchestration/       # Dynamic 7-step planner & multi-agent coordinator
│   ├── reports/             # Markdown, JSON, and interactive HTML exporters
│   ├── reviewers/           # 5 Specialist Sub-Agents (Security, Bugs, Arch, Perf, Test)
│   ├── schemas/             # Typed Pydantic schemas (Findings, Plan, Repo, Result)
│   ├── storage/             # Sandboxed workspace filesystem manager & memory/checkpoints
│   ├── verification/        # Verification Sub-Agent (false-positive elimination)
│   └── cli.py               # Rich CLI with review, inspect, plan, serve, evaluate, mcp
├── fixtures/
│   ├── vulnerable/          # Sample codebase with intentional test vulnerabilities
│   └── clean/               # Sample clean reference codebase
├── frontend/
│   └── index.html           # Interactive single-page web dashboard
├── reports/                 # Auto-generated review reports (.md, .json, .html)
├── tests/
│   ├── unit/                # Unit tests for API, CLI, verifier, schemas, storage, git, MCP, GitHub
│   ├── reviewers/           # Dedicated tests for each of the 5 specialist sub-agents
│   ├── evaluation/          # Evaluation benchmark tests
│   ├── agent/               # Agent execution tests
│   └── integration/         # Full multi-agent, API, and platform integration test pipelines
├── AGENTS.md                # Multi-agent architecture notes
├── Makefile                 # Make commands for build, test, and run
├── pyproject.toml           # Hatchling build specification & dependencies
└── README.md                # Project documentation & GitHub guide
```

---

## 🛡️ License
MIT License. Built for autonomous agentic code review workflows with **Pydantic Deep** and **Pydantic AI**.
