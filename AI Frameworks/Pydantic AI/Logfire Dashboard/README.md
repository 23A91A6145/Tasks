# AgentEval Lab 🔬

> **Production-Grade AI Evaluation, Observability & Regression Platform**  
> Built with [Pydantic AI](https://github.com/pydantic/pydantic-ai), [pydantic-evals](https://github.com/pydantic/pydantic-evals), [Logfire](https://logfire.pydantic.dev), and [FastAPI](https://fastapi.tiangolo.com).

---

## 🎯 Aim, Mission & Engineering Utility

### Why Traditional Unit Tests Fail on AI
Traditional software asserts `func() == expected`.  
AI systems are non-deterministic, multi-step, and prone to subtle regressions across prompt modifications, model upgrades, parameter tweaks, and tool schema alterations:

$$\text{Prompt / Model Iteration} \longrightarrow \text{Multi-Rubric Evaluation} \longrightarrow \text{Logfire Spans} \longrightarrow \text{Regression Engine} \longrightarrow \text{CI/CD Gate}$$

**AgentEval Lab** is a zero-cost-friendly, production-ready AI evaluation platform that automatically prevents degraded AI systems from reaching production.

---

## 🌟 Complete 5-Volume Platform Architecture

```
agenteval-lab/
├── api/                              # Production FastAPI Backend Service
│   ├── main.py                       # FastAPI application & Web UI server
│   └── routes/
│       ├── datasets.py               # Datasets listing, case inspection & slicing
│       ├── experiments.py            # Evaluation execution, matrix & experiment history
│       └── regressions.py            # Side-by-side comparison, trace inspection & incident ingestion
│
├── frontend/                         # Interactive Web UI Dashboard
│   └── index.html                    # High-contrast dark dashboard SPA (Vanilla JS/CSS)
│
├── app/                              # Customer Support Agent & Tools
│   ├── agent.py                      # Pydantic AI agent, FunctionModel & Live LLM dispatch
│   ├── config.py                     # Configuration & quality thresholds
│   ├── dependencies.py               # In-memory database (orders A100-H800, VIPs, FAQs)
│   └── tools.py                      # Order, customer, refund, discount, and FAQ tools
│
├── evals/                            # Evaluation & Observability Framework
│   ├── datasets/                     # 28 Curated Evaluation Cases, Slicing & Production Failures
│   ├── evaluators/                   # Deterministic, Behavioral, Multi-Rubric, and Cost Evaluators
│   ├── reports/                      # Timestamped JSON, Markdown, and Trace artifacts
│   ├── observability.py              # Logfire & OpenTelemetry hierarchical span manager
│   ├── dashboard.py                  # Terminal Observability Dashboard & ASCII Trend Line
│   ├── compare.py                    # Side-by-side experiment comparison & regression detector
│   ├── trace_debugger.py             # Trace-to-Failure root cause deep-dive inspector
│   ├── regression_engine.py          # Multi-Dimensional Regression Rule Engine (5 Dimensions)
│   ├── matrix_runner.py              # Model × Prompt Matrix Evaluation Runner
│   ├── cost_optimizer.py             # Token consumption & cloud expenditure calculator
│   ├── ci_gate.py                    # Automated CI/CD Quality Gate Runner
│   ├── production_feedback.py        # Production incident ingestion loop
│   ├── run_eval.py                   # Slicing CLI evaluation runner & quality gate
│   └── thresholds.py                 # Quality thresholds & regression rules
│
├── tests/                            # 49 Unit, Integration & API Tests (100% Passing)
│   ├── test_api.py                   # FastAPI REST endpoint integration tests
│   ├── test_agent.py                 # Tool execution, prompt injection, and agent tests
│   ├── test_behavioral.py            # Tool selection, argument accuracy, and prohibited tool tests
│   ├── test_ci_gate.py               # Automated CI gate pass/fail determination tests
│   ├── test_comparison.py            # Experiment delta calculations & regression flip tests
│   ├── test_dataset.py               # 28 cases, metadata integrity, and slicing filter tests
│   ├── test_evaluators.py            # Multi-rubric judge and hybrid engine composite score tests
│   ├── test_observability.py         # Logfire tracer and span lifecycle tests
│   ├── test_production_feedback.py   # Incident ingestion and verification tests
│   ├── test_regression.py            # Quality threshold violations & regression detection tests
│   └── test_regression_engine.py     # Quality, safety, and latency regression detection tests
│
├── scripts/                          # Executable Automation Shell Scripts
│   ├── start_server.sh               # Start FastAPI Web UI & API Server (Port 8000)
│   ├── run_matrix.sh                 # Run Model × Prompt Evaluation Matrix
│   ├── ci_gate.sh                    # Automated CI/CD regression quality gate runner
│   ├── ingest_feedback.sh            # Ingest production incidents into golden dataset
│   ├── run_regression_suite.sh       # Run targeted regression & safety suite
│   ├── run_eval.sh                   # Main evaluation runner script
│   ├── dashboard.sh                  # Launch terminal observability dashboard
│   ├── compare.sh                    # Side-by-side experiment comparison tool
│   ├── inspect_trace.sh              # Deep-dive into case traces
│   └── run_baseline.sh               # Baseline experiment runner
│
├── docs/                             # Engineering Architecture & Strategy Docs
├── .github/workflows/eval.yml        # Automated GitHub Actions CI workflow with quality gate
├── pyproject.toml                    # Dependencies and pytest configuration
└── README.md
```

---

## 🚀 Quickstart & Complete Commands Guide

### 1. Start the Interactive Web UI Dashboard & API Server

```bash
./scripts/start_server.sh
```
- 🌐 **Interactive Web UI Dashboard**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📖 **Interactive OpenAPI Documentation**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 2. Run Complete 28-Case Evaluation Suite

```bash
./scripts/run_eval.sh
# or: uv run python evals/run_eval.py
```

---

### 3. Run Model × Prompt Matrix Evaluation

```bash
./scripts/run_matrix.sh
# or: uv run python evals/matrix_runner.py
```

---

### 4. Run Automated CI/CD Regression Quality Gate

```bash
./scripts/ci_gate.sh
# or: uv run python evals/ci_gate.py --current latest
```

---

### 5. View Terminal Observability Dashboard & ASCII Quality Trends

```bash
./scripts/dashboard.sh
# or: uv run python evals/dashboard.py
```

---

### 6. Compare Historical Experiments Side-by-Side

```bash
./scripts/compare.sh
# or: uv run python evals/compare.py <baseline_report> <current_report>
```

---

### 7. Trace-to-Failure Deep-Dive Inspector

```bash
./scripts/inspect_trace.sh case_01
```

---

### 8. Ingest Production Incident into Golden Dataset

```bash
./scripts/ingest_feedback.sh --id PROD-9001 --prompt "Where is order A100?" --bad-output "I cannot find it." --expected "Order A100 is Shipped. Your tracking number is TRK-98765 for Noise-Cancelling Headphones."
```

---

### 9. Run Metadata Slicing Filters

```bash
# Slicing by Category
uv run python evals/run_eval.py --category safety
uv run python evals/run_eval.py --category boundary

# Slicing by Difficulty
uv run python evals/run_eval.py --difficulty hard

# Slicing by Risk Level
uv run python evals/run_eval.py --risk critical

# Slicing by Tag
uv run python evals/run_eval.py --tag refund
```

---

### 10. Run Full Pytest Suite (49 Unit & Integration Tests)

```bash
uv run pytest -v
```

---

## 📊 Visual CLI Output Highlights

### Model × Prompt Performance Matrix
```text
                  Model × Prompt Performance & Quality Matrix                   
┏━━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━┓
┃ Prompt Variant      │ Model   │    Pass │ Compos… │   Judge │     Avg │    Cost │ Quali… ┃
┃                     │ Under   │    Rate │   Score │   Score │ Latency │  ($/1k) │  Gate  ┃
┠─────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────────┨
┃ Prompt_V1_Standard  │ test    │  100.0% │    1.00 │    1.00 │   2.7ms │ $0.0000 │  PASS  ┃
┃ Prompt_V1_Standard  │ mock    │  100.0% │    1.00 │    1.00 │   2.7ms │ $0.0000 │  PASS  ┃
┃ Prompt_V2_Concierge │ test    │  100.0% │    1.00 │    1.00 │   2.6ms │ $0.0000 │  PASS  ┃
┃ Prompt_V2_Concierge │ mock    │  100.0% │    1.00 │    1.00 │   3.2ms │ $0.0000 │  PASS  ┃
┗━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━┛
```

### Trace-to-Failure Deep-Dive Inspector
```text
╭───────────────────────── Trace-to-Failure Inspector ─────────────────────────╮
│ Case: case_01_order_status_shipped | Category: normal | Risk: low | Status:  │
│ PASSED                                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
🔍 Execution Flow Trace (7.7ms)
├── 1. User Request / Prompt
│   └── Where is my order A100?
├── 2. Tool Invocations (1 calls)
│   └── lookup_order → args: {'order_id': 'A100'}
├── 3. Model Output
│   └── Order A100 is Shipped. Your tracking number is TRK-98765 for 
│       Noise-Cancelling Headphones.
└── 4. Expected Ground Truth
    └── Order A100 is Shipped. Your tracking number is TRK-98765 for 
        Noise-Cancelling Headphones.

                        Multi-Rubric Semantic Breakdown                         
╭────────────────────────┬──────────┬──────────┬───────────────────────────────╮
│ Rubric Dimension       │   Weight │    Score │ Feedback                      │
├────────────────────────┼──────────┼──────────┼───────────────────────────────┤
│ Accuracy Grounding     │      35% │     1.00 │ Fully grounded in real store  │
│ Relevance Completeness │      25% │     1.00 │ Directly addressed inquiry    │
│ Policy Compliance      │      25% │     1.00 │ Standard policy satisfied     │
│ Tone Security          │      15% │     1.00 │ Professional and compliant    │
╰────────────────────────┴──────────┴──────────┴───────────────────────────────╯
```

---

## 🏆 Project Completion & Verification Summary

- **Volumes 1–5**: 100% Completed, Tested & Validated.
- **Total Pytest Tests**: **49 tests (100% Passing in ~1.2s)**.
- **Hardware Efficiency**: Executes with **$0 inference cost**, ~2.5ms average latency per case on standard laptop CPU conditions without GPU requirements.
- **Production Readiness**: Full CI/CD quality gate enforcement, OpenTelemetry/Logfire span tracing, side-by-side regression detection, production feedback loop, FastAPI backend service, and interactive Web UI SPA.
