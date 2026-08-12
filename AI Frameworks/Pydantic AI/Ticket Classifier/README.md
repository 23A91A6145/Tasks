# Structured Ticket Classifier — Type-Safe AI Support Triage System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic AI](https://img.shields.io/badge/Pydantic%20AI-v2.28-E91E63.svg)](https://pydantic.dev)
[![Database](https://img.shields.io/badge/SQLite-3-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An expert, production-grade automated support ticket classification system built with **Pydantic AI**, **FastAPI**, and **SQLite**. It translates unstructured customer messages into validated, strictly typed objects representing categories, priorities, suggested agents, and triage metadata, ready for direct integration into enterprise databases or routing microservices.

---

## 🎯 Project Definition (Aim, Uses, What, Where, How, When, Why)

### 1. What is this project?
The **Structured Ticket Classifier** is a type-safe AI pipeline that intercepts unstructured support requests and processes them into structured data. Instead of returning raw, variable natural language text, it forces the AI to output an object that conforms to a strict Pydantic schema, validating values against pre-defined Enums (categories, priority levels, and routing destinations).

```
Unstructured Ticket Text
         ↓
    Pydantic AI
         ↓
   Local Ollama / LLM
         ↓
  Structured Schema (ToolOutput)
         ↓
Pydantic Validation (Retries if invalid)
         ↓
  Validated Result Object
         ↓
 API / Database / Front-end Dashboard
```

### 2. Why do we need it?
Traditional support classification depends on fragile keyword matching (`if "refund" in message`) or raw text outputs from LLMs (`"The category is billing."`). Keyword matching misses semantic intent, while raw LLM strings are prone to hallucinating formats, leaking information, or changing structures unpredictably, breaking downstream application logic. 
By using Pydantic AI's `output_type` constraint, we enforce a typed contract. If the LLM returns an invalid value, the framework automatically retries or rejects it, guaranteeing that the database and downstream services only receive valid data.

### 3. Aim & Core Objectives
*   **Zero-Cost Execution**: Engineered to run locally on consumer hardware (e.g., Ubuntu Linux, 16GB RAM, no GPU) using quantized models in **Ollama** (`qwen2.5-coder:7b` or `llama3.2:3b`).
*   **Resiliency**: Features a multi-layered classification strategy with automatic LLM validation retries and a deterministic, keyword-based local fallback classifier to guarantee uptime.
*   **Security (Prompt Injection Defense)**: Protects the classifier against adversarial instructions (e.g., tickets containing instructions to override classification rules).
*   **Enterprise Architecture**: Includes database persistence (SQLite), background analytics tracking, a REST API (FastAPI), unit/integration test suites, and a polished dark-mode front-end dashboard.

### 4. Real-World Applications & Uses
*   **Support Ticket Routing**: Instantly routes billing inquiries, security breaches, and technical errors to the respective support queues.
*   **SLA Enforcement**: Detects priority levels ('critical', 'high') to trigger escalation workflows (e.g., PagerDuty, Slack alerts).
*   **GDPR/Privacy Redaction**: Identifies and flags security or account erasure requests for immediate human review.
*   **Support Analytics**: Generates graphs on category frequency, response times, and automated resolution rates.

---

## 📦 Project Architecture

```
structured-ticket-classifier/
├── app/
│   ├── __init__.py          # Package initialization & exports
│   ├── agent.py             # Pydantic AI agent, system prompts & fallback logic
│   ├── config.py            # Environment configurations (dotenv, paths, models)
│   ├── database.py          # SQLite connections, schema initialization & analytics
│   ├── models.py            # Pydantic schemas (enums, TicketResult definition)
│   ├── prompts.py           # Core system prompts and safety rules
│   └── static/
│       └── index.html       # Single-page HTML/CSS/JS frontend dashboard
├── data/
│   └── sample_tickets.json  # Benchmark dataset of support tickets
├── tests/
│   ├── __init__.py
│   ├── test_agent.py        # Mocks, fallback tests, agent overrides
│   ├── test_cases.py        # FastAPI endpoints & database metrics tests
│   └── test_models.py       # Pydantic validation and constraint tests
├── .env                     # Environment variables (Git-ignored)
├── .gitignore               # Excluded file paths
├── pyproject.toml           # PEP 621 package metadata & dependencies
└── main.py                  # CLI and server runner entrypoint
```

---

## 🔌 API Endpoints Reference

The FastAPI server exposes the following endpoints for integration with external ticketing platforms or dashboards:

*   **`GET /api/v1/health`** — Performs system health checks, returning current LLM config and environment name.
*   **`POST /api/v1/tickets/classify`** — Triages an incoming ticket. Parses categories/priorities/agents, stores the result, and returns validated JSON metadata.
*   **`GET /api/v1/tickets`** — Retrieves a list of the 50 most recent classified tickets from SQLite (supports pagination via `limit` and `offset` query params).
*   **`GET /api/v1/metrics`** — Computes real-time statistics (total tickets, categories/priorities distribution, human review rates, average confidence, and latency).
*   **`POST /api/v1/tickets/{ticket_id}/reclassify`** — Overrides a classification manually (human-in-the-loop audit logs). Takes `category`, `priority`, and `suggested_agent` payloads and updates the database, setting `is_reclassified` to `true`.

---

## 🛠️ Installation & Setup (Laptop Specs: Ubuntu OS, 16/512)

This project is fully optimized for standard laptop conditions (Ubuntu 24.04/26.04 LTS, i7 CPU, 16GB RAM, No GPU).

### 1. Prerequisites
Ensure python 3.10+ and `uv` (a fast Python package installer and manager) are installed:
```bash
python3 --version
uv --version
```
*If `uv` is not installed, install it using:*
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Configure Local LLM (Ollama)
For CPU-only machines, use Ollama with small, high-performance models.
```bash
# Verify Ollama is running
ollama --version

# Pull the primary recommended model (excellent for code/reasoning)
ollama pull qwen2.5-coder:7b

# Pull the lightweight model (extremely fast on CPU)
ollama pull llama3.2:3b
```

### 3. Initialize the Virtual Environment & Dependencies
All libraries are configured in `pyproject.toml`. Run the following command in the project root:
```bash
# Installs python virtual environment (.venv) and all locked packages
uv sync
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
# Mode config
ENV=production
DEBUG=false

# LLM Configuration
# Options: "ollama:qwen2.5-coder:7b", "ollama:llama3.2:3b", "groq:llama-3.3-70b-versatile", "google:gemini-1.5-flash"
LLM_MODEL=ollama:qwen2.5-coder:7b
FALLBACK_MODEL=ollama:llama3.2:3b

# Ollama Endpoint Configuration
OLLAMA_BASE_URL=http://localhost:11434/v1

# Cloud Provider API Keys (Optional, uncomment and fill to use Groq/Gemini)
# GROQ_API_KEY=gsk_...
# GOOGLE_API_KEY=AIzaSy...
```

---

## 🚀 Execution & Command-Line Guide

All commands should be executed from the project root using `uv run`.

### 1. Initialize the SQLite Database
```bash
uv run python main.py init-db
```
*Creates `tickets.db` and configures the database schema.*

### 2. Start the FastAPI Web Server
```bash
# Starts the FastAPI server and mounts the HTML frontend
uv run python main.py server
```
*   **Web Dashboard URL**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
*   **Swagger API Docs**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test endpoints interactively.

### 3. Classify a Ticket via the CLI
You can test the classifier directly from your terminal:
```bash
uv run python main.py classify "Hi, my payment method failed but I was charged twice. Help!"
```
**Expected JSON Output:**
```json
{
  "database_id": 1,
  "category": "billing",
  "secondary_category": null,
  "priority": "high",
  "suggested_agent": "billing_agent",
  "confidence": 0.98,
  "summary": "Charged twice despite payment method failure.",
  "requires_human_review": false,
  "reasoning": "Ticket reports duplicate billing transaction following a failure alert.",
  "processing_time_ms": 284,
  "model_used": "ollama:qwen2.5-coder:7b"
}
```

### 4. Query Triage Metrics via the CLI
```bash
uv run python main.py metrics
```

### 5. Run the Accuracy & Latency Benchmark
Evaluate the classifier's performance against the reference dataset in `data/sample_tickets.json`:
```bash
# Run using fast, deterministic rule heuristics (default, free)
uv run python main.py evaluate --mode fallback

# Run using the mocked TestModel
uv run python main.py evaluate --mode test

# Run using the real configured LLM (requires Ollama to be running)
uv run python main.py evaluate --mode llm
```
*Generates a comprehensive precision and latency report in `evaluation_results.md`.*

---

## 🧪 Testing Harness & Verification

We use `pytest` to run our unit, integration, and API test suites. The tests run 100% locally and deterministically, utilizing `pydantic_ai.models.test.TestModel` to mock LLM interactions. No API calls or local Ollama inferences are executed during testing.

### Run all tests
```bash
uv run pytest -v
```

### Test Coverage Areas
1.  **Schema Constraints (`tests/test_models.py`)**: Checks validator boundaries, invalid enums, and confidence ranges (0.0 to 1.0).
2.  **Fallback Heuristics (`tests/test_agent.py`)**: Verifies that when the agent is bypassed or encounters errors, the rule-based backup properly flags critical security issues, assigns agents, and maps priorities.
3.  **Mock Pipeline Execution (`tests/test_agent.py`)**: Uses `agent.override()` to mock structured output generation.
4.  **API & Database Integration (`tests/test_cases.py`)**: Uses FastAPI `TestClient` to verify `/classify`, `/tickets`, and `/metrics` response codes, JSON schema matches, and SQLite metric aggregations.

---

## 🔮 Roadmap & Future Enhancements (Next Phase)

Now that the implementation through **Volume 4** (Pydantic validation, multi-model LLM fallback routing, SQLite storage, FastAPI endpoints, a responsive frontend, TestClient suites, and secondary multi-intent categorizations) is fully completed and verified, the next phase should focus on:

1.  **Production API Failover**: Set up a Vertex AI or Google Gemini API as the primary fallback endpoint for low-latency queries if local Ollama servers are overloaded.
2.  **Fine-Grained Confidence Calibration**: Introduce self-evaluation check questions inside the prompt to calibrate raw model confidence scores dynamically.
3.  **Asynchronous Triage Pipelines**: Integrate Celery or FastAPI background tasks for processing bulk ticket triage inputs asynchronously.
4.  **Multi-Agent Routing (Volume 5/6)**: Build specific downstream agents (e.g., automated refund processor agent) triggered by the classifier's output metadata.
5.  **Analytics Visualizations**: Add charting libraries to the web page to monitor category and priority metrics graphically.
