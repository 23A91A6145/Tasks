# 📘 Groq vs Ollama Benchmark (Microsoft Agent Framework)

> **Provider Swap Benchmarking System** — A production-grade AI performance evaluation and provider abstraction platform built on Microsoft Agent Framework concepts.

---

## 🎯 Aim & Goal
The primary aim of this project is to evaluate and compare the performance, latency, throughput, quality, and reliability of running identical AI agents using **Groq** (cloud-accelerated LPU inference) vs **Ollama** (local desktop/server inference).

By changing only the backend `ChatClient` while preserving the exact `ChatAgent` instructions, system prompt, and tools, this framework provides a zero-bias, data-driven evaluation mechanism for engineering teams making model/provider selection decisions.

---

## 💡 What, Why, Where, How & When

### 1. What is this?
An AI Provider Benchmarking Suite that runs standardized prompt datasets across multiple LLM backends (Groq, Ollama, and extensible OpenAI-compatible providers) through Microsoft Agent Framework abstractions, collecting timing, token usage, throughput, and response quality metrics.

### 2. Why build this?
- **Avoid Vendor Lock-In:** Decouple agent logic from underlying LLM providers.
- **Cost vs Performance Optimization:** Determine when local inference (Ollama - $0 cost) is sufficient vs cloud LPUs (Groq - low latency).
- **Production AI Evaluation:** Provide actionable metrics (TTFT, tokens/sec, latency, quality score) rather than subjective impressions.

### 3. Where is it used?
- **Laptop / Local Development:** Benchmarking local Ollama models (e.g. `llama3.2:1b`, `llama3.3:70b`, `qwen2.5:7b`, `phi3`) against cloud APIs.
- **CI/CD Pipelines:** Automated regression testing for LLM quality and response consistency.
- **Enterprise Architecture:** Evaluating model deployment options (On-Premise vs Cloud).

### 4. How does it work?
1. The **Benchmark Controller** loads prompt test suites (`datasets/prompts.csv`, `datasets/benchmark_cases.json`).
2. The **Provider Manager** initializes provider backends (`GroqClient`, `OllamaClient`, `MockClient`).
3. The **ChatAgent** executes prompts across providers with identical system instructions.
4. The **Metrics Collector** captures precise timings, token counts, and error rates.
5. The **Dashboard & Evaluator** exports structured CSV/JSON results and visual reports.

### 5. When to use?
- Selecting a model backend for new agent deployments.
- Auditing API cost and latency SLA compliance.
- Testing local fallback reliability when cloud providers experience downtime.

---

## 🏗️ System Architecture

```
                       User Prompts / Datasets
                                  │
                                  ▼
                        Benchmark Controller
                                  │
          ┌───────────────────────┴───────────────────────┐
          │                                               │
          ▼                                               ▼
    Groq ChatClient                                Ollama ChatClient
          │                                               │
          ▼                                               ▼
       Same ChatAgent (Instructions, Persona, Tools)
          │                                               │
          ▼                                               ▼
                   Results Collector & Evaluator
                                  │
                                  ▼
                   CSV • JSON • Charts • CLI Report
```

---

## 🗂 Project Structure

```
Gork vs Ollama/
├── app/
│   ├── __init__.py         # Package initialization
│   ├── agent.py            # ChatAgent wrapper using Agent Framework
│   ├── providers.py        # Provider Swap Layer (Groq, Ollama, Mock)
│   ├── benchmark.py        # Benchmark Execution Engine
│   ├── evaluator.py        # Response quality & metric evaluator
│   ├── metrics.py          # Metric collection & timing utilities
│   ├── reports.py          # Summary report generation
│   ├── config.py           # Configuration & environment loader
│   └── utils.py            # Helper formatting & logger utilities
│
├── datasets/
│   ├── prompts.csv         # Categorized prompt dataset
│   └── benchmark_cases.json# Structured benchmark test cases
│
├── results/
│   ├── benchmark.csv       # Execution CSV output
│   ├── benchmark.json      # Complete JSON run records
│   ├── charts/             # Generated visual benchmark graphs
│   └── reports/            # Summary text reports
│
├── logs/
│   ├── benchmark.log       # Application logs
│   └── error.log           # Error logs
│
├── docs/
│   ├── architecture.md     # Deep-dive system design
│   └── methodology.md    # Benchmarking evaluation methodology
│
├── .env                    # Runtime environment configuration
├── .env.example            # Environment template
├── requirements.txt        # Python dependency manifest
├── Dockerfile              # Docker container setup
├── docker-compose.yml      # Orchestration config
├── README.md               # Main project documentation
└── main.py                 # CLI Entry Point
```

---

## 🚀 Quick Start (Volume 1 Setup)

### Step 1: Environment Setup
```bash
# Create python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration
Copy `.env.example` to `.env` and set your API keys if available (Groq is free, Ollama runs locally):
```bash
cp .env.example .env
```

### Step 3: Run Provider Health Check & Volume 1 CLI
```bash
python main.py --check-providers
```

Or run a dry-run benchmark test:
```bash
python main.py --mode dry-run
```

---

## 📊 Volume Deliverables & Completion Status

- [x] **Volume 1 — Foundation:** Planning, Environment virtualenv manifest, Pydantic/dotenv config loader.
- [x] **Volume 2 — Benchmark Engine:** Provider swapping interfaces, ChatAgent wrapper, telemetry counters.
- [x] **Volume 3 — Evaluation Dashboard:** Automated ResponseEvaluator, Matplotlib analytics rendering, Markdown scorecards.
- [x] **Volume 4 — Production Benchmark Suite:** Sequential CPU-safe execution, linear backoff retries, `/proc/meminfo` RAM tracking.
- [x] **Volume 5 — Deployment:** Docker containment (`Dockerfile`), docker-compose mounts, and extra_hosts mappings.

---

## ⚡ Laptop CPU comparative Scorecard (Actual Results)

Running on **16GB RAM, CPU-only Linux Laptop** environment (Ollama `llama3.2:3b` model fallback):

| Provider | Model ID | Latency (Avg) | TTFT (Avg) | Throughput (TPS) | Quality Score (Avg) | RAM footprint | Success Rate |
|---|---|---|---|---|---|---|---|
| **Ollama (Local)** | `llama3.2:3b` | **15.66s** | **1.39s** | **10.5 tps** | **10.0/10** | **5.34 GB / 5.34 GB** | **100%** |
| **Groq (Cloud)** | `llama-3.3-70b` | *No Key* | *No Key* | *No Key* | *No Key* | *No Key* | *Skipped* |

---

## 🐳 Docker Deployment Instructions

Run the benchmarking suite inside a container to isolate dependencies:

### 1. Build and Run via Compose (Recommended)
This maps directory results and routes host port requests automatically:
```bash
# Build and run dry-run benchmark
docker-compose up --build
```

### 2. Output Retrieval
Once completed, check the generated assets directly on your host machine:
*   Reports: `results/reports/summary_report.md`
*   Matplotlib Visualizations: `results/charts/`

---

## 📜 License
MIT License - Open Source & Free for Enterprise / Research usage.
