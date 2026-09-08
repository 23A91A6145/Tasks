# 🚀 StackPilot: Autonomous Technology Migration & Architecture Advisor
## Production Planner–Executor–Critic–Replanner Agent Platform
### Master Architecture Specification & 5-Volume Implementation Plan

---

## 1. Executive Summary & Core Mission

### 1.1 Project Aim
**StackPilot** is an autonomous, stateful engineering advisory system engineered with **LangGraph**, **FastAPI**, and **React/TypeScript**. It is purpose-built to solve complex, non-deterministic enterprise challenges:
> *"Given a company's legacy code repositories, database schemas, deployment manifests, operational constraints, and strategic migration targets, autonomously inspect the stack, plan analytical tasks, execute static and dependency audits, critique findings, dynamically replan when encountering gaps or failures, request human intervention before risky operations, and synthesize a mathematically and architecturally grounded migration roadmap."*

Unlike fragile linear chains or naive single-prompt LLM wrappers, StackPilot embodies the **Planner–Executor–Critic–Replanner** agentic paradigm. It actively handles partial observability, environmental tool failures, ambiguous schemas, conflicting constraints, and budgetary boundaries without hallucinating or entering infinite loops.

```
                                  ┌───────────────┐
                                  │  User Goal &  │
                                  │  Constraints  │
                                  └───────┬───────┘
                                          ▼
                                  ┌───────────────┐
                                  │    PLANNER    │◄─────────────────┐
                                  │ (Decompose &  │                  │
                                  │   Sequence)   │                  │
                                  └───────┬───────┘                  │
                                          ▼                          │
                                   Structured Plan                   │
                                          │                          │
                                          ▼                          │
                        ┌──────────────────────────────────┐         │
                        │             EXECUTOR             │         │
                        │  (Safe Tool Dispatch & Parse)    │         │
                        └─────────────────┬────────────────┘         │
                                          │                          │
                                    Task Evidence                    │
                                          ▼                          │
                                  ┌───────────────┐                  │
                                  │    CRITIC     │                  │
                                  │ (Evaluate &   │                  │
                                  │ Gap Analysis) │                  │
                                  └───────┬───────┘                  │
                                          ▼                          │
                                    Passing Grade?                   │
                                    /            \                   │
                           YES    /                \   NO            │
                                ▼                    ▼               │
                      ┌──────────────────┐  ┌──────────────────┐     │
                      │   SYNTHESIZER    │  │    REPLANNER     │─────┘
                      │ (Evidence-Backed │  │ (State Patch &   │
                      │  Recommendation) │  │  Delta Mutation) │
                      └──────────────────┘  └──────────────────┘
```

---

## 2. Core Engineering & System Design Principles

### 2.1 Agent vs. Workflow (Why LangGraph?)
* **Workflow:** Pre-determined linear pipeline ($A \rightarrow B \rightarrow C$). Any failure stops the run.
* **Agent:** Stateful, dynamic loop driven by intermediate discoveries. The agent decides what to execute next based on the observed evidence.

### 2.2 Why Replanning?
Pre-flight plans are inherently incomplete. Discovered architectural coupling, tool timeouts, or constraint conflicts require dynamic adaptation without discarding previous progress.

### 2.3 Preventing Infinite Loops
1. Bounded execution limit (`max_replans = 3`, `max_steps = 15`).
2. Exponential backoff on transient tool failures.
3. Checkpoint cycle detection comparing plan state hashes.

### 2.4 Human-in-the-Loop (HITL) Guardrails
Using LangGraph's native `interrupt()` feature, any task flagged with `risk_level == "HIGH"` suspends graph execution until a human administrator approves, modifies, or rejects the action.

---

## 3. Technology Stack & Zero-Cost Ubuntu Environment

| Component | Choice | Zero-Cost Details |
| :--- | :--- | :--- |
| **OS** | Ubuntu 22.04 / 24.04 LTS | Standard Linux environment |
| **Hardware** | 16 GB RAM / CPU-only | Lightweight quantized models consume $< 3.5\text{ GB}$ RAM |
| **Local LLM** | Ollama (`qwen2.5:3b` / `llama3.2:3b`) | 100% free, runs offline at $\approx 30\text{ tps}$ |
| **Cloud Fallback** | Google Gemini / Groq free tier | Zero cost API evaluation testing |
| **Orchestration**| LangGraph v0.2+ | StateGraph, Checkpoints, Interrupts |
| **Backend** | FastAPI (Async) + Uvicorn | High-performance Python async backend |
| **Frontend** | React 18 + TypeScript + Vite | Cybernetic dark UI with Tailwind CSS |
| **Graph UI** | React Flow (`@xyflow/react`) | Interactive live node graph visualizer |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Durable graph state persistence |

---

## 4. 5-Volume Implementation Roadmap

### 📘 Volume 1: Foundation & Domain Design (Phases 1–5)
1. **Phase 1: Domain Modeling & Threat Matrix** (`docs/threat-model.md`, `AgentState` schema).
2. **Phase 2: Ubuntu Dev Environment & Ollama Setup** (`qwen2.5:3b` configuration).
3. **Phase 3: Backend Project Setup & FastAPI Skeleton** (`main.py`, lifespan, CORS).
4. **Phase 4: Relational Data Models** (SQLModel schemas for projects, runs, tasks).
5. **Phase 5: Frontend Scaffold & Tailwind Design System** (React, Vite, dark cybernetic palette).

### 📗 Volume 2: The Agent Brain (Phases 6–10)
6. **Phase 6: Typed Agent State & Graph Topology** (`StateGraph`, conditional edges).
7. **Phase 7: Planner Agent & Structured Outputs** (Pydantic `TaskPlan` schema).
8. **Phase 8: Safe Tool Registry** (AST analyzer, SQL parser, dependency auditor, cost estimator).
9. **Phase 9: Critic Agent & Gap Analysis** (Evidence validation, completeness scoring).
10. **Phase 10: Replanner Agent & Delta Plan Mutation** (State-preserving recovery loop).

### 📙 Volume 3: Resilience, Checkpoints & HITL (Phases 11–15)
11. **Phase 11: State Persistence & Time-Travel Debugging** (`AsyncSqliteSaver`, rollback endpoint).
12. **Phase 12: Tool Retries, Exponential Backoff & Chaos Testing**.
13. **Phase 13: Two-Tier Memory** (Short-term working state + Long-term project preferences).
14. **Phase 14: Human-in-the-Loop Interrupts** (`interrupt()`, approve/edit/reject workflows).
15. **Phase 15: Evaluation Harness & 50-Scenario Benchmark** (Automated quality rubric).

### 📕 Volume 4: Production Application & Hardening (Phases 16–20)
16. **Phase 16: Real-Time SSE Event Pipeline** (Live node transitions and log streaming).
17. **Phase 17: Interactive Execution Graph Viewer** (React Flow canvas, state inspector).
18. **Phase 18: Security Hardening & OWASP Top 10 Protections** (Path validation, rate limiting).
19. **Phase 19: Comprehensive Observability & Telemetry** (OpenTelemetry, Prometheus metrics).
20. **Phase 20: Dockerized Multi-Service Deployment** (`docker-compose.yml`, health checks).

### 📓 Volume 5: Advanced Intelligence, MCP & Portfolio (Phases 21–25)
21. **Phase 21: Real Repository Analyzers** (Treesitter AST, Docker, Terraform parsers).
22. **Phase 22: Migration Strategy Engine & Radar Matrix** (Tradeoff analysis).
23. **Phase 23: Interactive "What-If" Simulation Playground** (Dynamic parameter re-run).
24. **Phase 24: Model Context Protocol (MCP) Integration** (Standardized tool server clients).
25. **Phase 25: Master Portfolio Assets & Architecture Defense** (ADRs, demo walkthrough).
