# AGENTS.md — DeepRepo Multi-Agent Architecture & Context

## 🎯 Overview
DeepRepo Reviewer is an autonomous software-engineering multi-agent platform built on **Pydantic Deep** and **Pydantic AI**. It operates on real Git repositories and diffs to inspect codebases, plan multi-step reviews, isolate filesystem operations, execute specialized checks, verify citations against real code, learn persistent context memory, and output typed findings via CLI, REST API, Web UI, and MCP server.

---

## 🤖 Agent Topology

### 1. Lead Deep Agent (`DeepRepoReviewer`)
- **Role:** Autonomous Orchestrator & Planner
- **Core Primitives:** `create_deep_agent()`, `LocalBackend`, `TodoToolset`, `ReviewerDeps`
- **Capabilities:**
  - Profiles repository structure and dependencies.
  - Compiles a dynamic step-by-step review plan.
  - Coordinates domain analysis and enforces evidence extraction.
  - Aggregates findings and calculates composite risk levels.

### 2. Specialized Reviewers (Implemented & Active in Volumes 3–5)
- **Security Reviewer (`SecurityReviewer`):** Vulnerability discovery (SQLi, Auth bypass, Hardcoded secrets, Command Injection, Insecure Deserialization, SSRF, SSL bypass, Permissive CORS).
- **Architecture Reviewer (`ArchitectureReviewer`):** Modular boundaries, circular dependencies, monolithic modules, global mutable state, cyclomatic complexity.
- **Bug & Logic Reviewer (`BugReviewer`):** Unhandled exceptions, mutable default traps, identity check traps, bare excepts, resource leaks.
- **Performance Reviewer (`PerformanceReviewer`):** Computational bottlenecks, N+1 queries, blocking synchronous calls (`time.sleep`, `requests`) in async def routines, string concatenation loops.
- **Test Reviewer (`TestReviewer`):** Missing assertions, empty stub tests, dummy assertions, missing test files in changeset.
- **Verification Agent (`VerificationAgent`):** Validates line numbers and cited code snippets against the real filesystem to eliminate false positives and calculate precision rates.
- **Review Coordinator (`ReviewCoordinator`):** Dynamically dispatches specialist agents in parallel via `asyncio.gather()`, aggregates and deduplicates findings, calculates composite risk scores.

### 3. Production & Integration Layer
- **Persistent Project Memory (`ProjectMemory`):** Stores architectural rules, intentional exceptions, and false-positive suppressions across review runs in `.deeprepo/memory.json`.
- **Fault-Tolerant Checkpoints (`ReviewCheckpointManager`):** Saves snapshot state after each phase to enable instant recovery.
- **Model Context Protocol (`DeepRepoMCPServer`):** Standard MCP server exposing review tools and resources for Claude Desktop, Cursor, Antigravity, and OpenCode.
- **GitHub PR Automation (`GitHubPRReviewer`):** Formats GitHub PR reviews, passes/blocks check runs, and builds GitHub Check Annotations.
- **DevSecOps Benchmark (`EvaluationBenchmark`):** Ground-truth benchmark suite evaluating precision, recall, and F1 score.

---

## 🔒 Safety & Resource Constraints
- **Ubuntu 16GB RAM / 512GB SSD Optimization:** Memory-bounded file reads (512 KB limit per file), streaming diff inspection, non-blocking asynchronous execution.
- **Filesystem Isolation:** Workspace boundary enforcement prevents path traversal (`../../`) and blocks access to sensitive files (`.env`, private keys, secrets).
- **Auto-Confirm Execution:** Fully non-blocking CLI and API execution without manual prompts.

---

## 🛠️ CLI Entrypoints
- `deeprepo test-env`: Verify environment and dependencies.
- `deeprepo inspect <path>`: Profile repository metadata and Git status.
- `deeprepo plan <path>`: Generate an autonomous step-by-step review plan.
- `deeprepo review <path> [--auto-confirm]`: Execute full multi-agent review and output Markdown, JSON, and HTML reports.
- `deeprepo serve [--port 8000]`: Launch FastAPI REST API server and interactive Single-Page Web Dashboard.
- `deeprepo evaluate`: Run ground-truth DevSecOps benchmark suite.
- `deeprepo mcp`: Start Model Context Protocol (MCP) stdio server.
- `deeprepo memory <path>`: Inspect and manage persistent repository memory.
