# Support Triage Crew — Complete Plan

A **multi-agent AI customer support triage system**: classify → route → specialize → validate → deliver.

**Zero cost, zero API keys, zero cloud.** Runs entirely on your machine.

---

## 1. What This Is

```
User says: "I was charged twice!"
    │
    ▼
┌─────────────────┐
│  Router         │──→ "billing"
│  (classifies)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌───────────────┐     ┌───────────────┐
│  Billing Agent  │────→│  Validator    │────→│  Response     │
│  + Currency     │     │  (5 checks)   │     │  + SQLite log │
│  + Company Data │     │  max 1 retry  │     │               │
└─────────────────┘     └───────────────┘     └───────────────┘
```

| Agent | Handles | Tools |
|-------|---------|-------|
| Router | Classifies query → billing/technical/sales/escalate | None |
| Billing | Charges, invoices, refunds, subscriptions | Currency Converter, Company Data |
| Technical | Login errors, bugs, crashes, configuration | Web Search, Calculator |
| Sales | Plans, pricing, comparisons, upgrades | Web Search, Company Data, Weather |
| Validator | Quality checks: completeness, accuracy, tone, actionability, conciseness | None |

### Demo Mode (No LLM Needed)

When `USE_DEMO_LLM=true` (default), the system bypasses AI entirely:
- **Keyword matching** classifies the query (billing/technical/sales/escalate)
- **Canned responses** return realistic support answers
- **Full pipeline works** — CLI, Web UI, API — without any LLM installed

---

## 2. Where Everything Is

```
Project: /home/cherry/Desktop/1_Gen/Tasks/Crew/Support Triangle

Files (47 total):
├── main.py                 CLI entry point
├── config/
│   ├── settings.py         10 env vars
│   ├── agents.yaml         Agent definitions
│   └── tasks.yaml          Task definitions
├── tools/
│   ├── demo_llm.py         Demo classifier + canned responses
│   ├── calculator.py       AST evaluator
│   ├── web_search.py       DuckDuckGo
│   ├── custom_api.py       Weather + Currency
│   └── company_data.py     Mock data
├── crews/
│   └── support_crew.py     Pipeline: demo or real
├── api/
│   ├── fastapi_app.py      8 endpoints
│   └── history_store.py    SQLite
├── ui/
│   └── streamlit_app.py    Web interface
├── tests/                  (77 tests)
├── examples/
│   └── SUPPORT_QUERIES.md  20 sample queries
├── .env                    Active config
├── .env.example            Template
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── README.md
├── PLAN.md                 ← You are here
└── FINAL_CONCLUSION.md     Technical reference
```

---

## 3. Quick Start (3 Ways)

### Prerequisites
```bash
cd /home/cherry/Desktop/1_Gen/Tasks/Crew/Support Triangle
pip install -r requirements.txt  # 9 dependencies
```

**Demo mode is on by default** (`USE_DEMO_LLM=true` in `.env`). No LLM needed.

### Interface A: CLI
```bash
# Single query
python main.py "I was charged twice"

# Demo mode — 9 example queries
python main.py --demo
```

### Interface B: Web UI
```bash
streamlit run ui/streamlit_app.py
# → http://localhost:8501
```

### Interface C: API
```bash
uvicorn api.fastapi_app:app --port 8000
# → http://localhost:8000/docs
```

---

## 4. Complete Example Walkthrough

### Example: "I was charged twice"

**Step 1: CLI**
```
$ python main.py "I was charged twice"

============================================================
 Classification: BILLING
 Tools: Currency Converter, Company Data
 Validated: YES
------------------------------------------------------------
Thank you for reaching out about this billing concern.

I have reviewed your account and see what happened.
...
============================================================
```

**Step 2: Web UI**
1. `streamlit run ui/streamlit_app.py`
2. Open http://localhost:8501
3. Type "I was charged twice" in the chat input
4. See: agent badge (💳 BILLING), tool badges, validation ✓
5. Click 👍 or 👎 to give feedback
6. Switch to **History** tab to see all conversations
7. Switch to **Settings** tab to see stats

**Step 3: API**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "I was charged twice"}'
```
Response:
```json
{
  "id": 1,
  "conversation_id": "conv_abc123...",
  "query": "I was charged twice",
  "classification": "billing",
  "tools_used": ["Currency Converter", "Company Data"],
  "response": "Thank you for reaching out about this billing concern...",
  "validated": true,
  "execution_time": 0.01
}
```

---

## 5. Detailed Interface Guides

### CLI (`python main.py`)

| Command | What Happens |
|---------|-------------|
| `python main.py "help"` | Classifies, routes, responds, prints result |
| `python main.py --demo` | Runs 9 pre-defined queries, shows each result |
| `python main.py "my query" --demo` | `--demo` is ignored, single query runs |

Output format:
```
============================================================
 Classification: TECHNICAL
 Tools: Web Search, Calculator
 Validated: YES
 Report: (only shown if validation failed)
------------------------------------------------------------
[full response text]
============================================================
```

Expected classifications for demo queries (9/9 correct):
| Query | Expected | Demo Result |
|-------|----------|-------------|
| "I was charged twice..." | billing | ✅ billing |
| "I can't log into my account..." | technical | ✅ technical |
| "Compare Pro vs Enterprise..." | sales | ✅ sales |
| "How do I reset my password?" | technical | ✅ technical |
| "Student discounts on basic?" | billing | ✅ billing |
| "Invoice #1243 shows wrong amount" | billing | ✅ billing |
| "Dashboard widget keeps loading" | technical | ✅ technical |
| "Upgrade from Basic to Pro?" | sales | ✅ sales |
| "Can I speak to a human?" | escalate | ✅ escalate |

### Web UI (`streamlit run ui/streamlit_app.py`)

| Tab | Features |
|-----|----------|
| **💬 Chat** | Chat input, welcome card on first visit, agent badge, tool badges, validation status, execution time, feedback 👍/👎, processing indicator |
| **📋 History** | Search by keyword, filter by category, page size selector, CSV export, expandable response view |
| **⚙️ Settings** | LLM config display, system stats (total/routed/validated/avg time/feedback counts), bar chart by category |

Sidebar controls:
- **New Chat** button — clears conversation, starts fresh
- **Clear History** button — deletes all stored data
- Shows current LLM and conversation count

### API (`uvicorn api.fastapi_app:app --port 8000`)

8 endpoints:

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/health` | Status check | `curl localhost:8000/health` → `{"status":"ok","version":"1.1.0"}` |
| POST | `/chat` | Process query | `curl -X POST localhost:8000/chat -H "Content-Type: application/json" -d '{"query":"help"}'` |
| GET | `/history` | Paginated history | `curl "localhost:8000/history?limit=10&offset=0&classification=billing&search=charge"` |
| GET | `/history/{id}` | Single entry | `curl localhost:8000/history/1` |
| POST | `/history/{id}/feedback` | Thumbs up/down | `curl -X POST localhost:8000/history/1/feedback -H "Content-Type: application/json" -d '{"feedback":1}'` |
| DELETE | `/history/{id}` | Delete entry | `curl -X DELETE localhost:8000/history/1` |
| GET | `/export` | Export all | `curl "localhost:8000/export?format=csv"` or `?format=json` |
| GET | `/stats` | System stats | `curl localhost:8000/stats` |

Multi-turn conversation example:
```bash
# First turn
curl -X POST localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"I have a billing problem"}'
# → conversation_id: "conv_abc123"

# Second turn (same conversation)
curl -X POST localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"It charged me twice","conversation_id":"conv_abc123"}'
# → Agent sees the previous exchange as context
```

---

## 6. Expected Behaviors & Edge Cases

### Demo Mode Behavior
| Situation | What Happens |
|-----------|-------------|
| Normal query with keywords | Classified and responded to instantly |
| Query with no matching keywords | Classified as "escalate" |
| Very long query (>2000 chars) | Truncated at API level (Pydantic validation) |
| Empty query | API returns 422 validation error |
| `--demo` flag | Sets USE_DEMO_LLM=true, runs 9 queries |
| Streamlit first visit | Shows welcome card with category badges |
| History search with no matches | Shows "No conversation history yet" |
| Export with no data | Returns empty JSON array or CSV with header only |

### Real LLM Mode Behavior (if Ollama is installed)
| Situation | What Happens |
|-----------|-------------|
| Ollama running | Full AI pipeline with classification + response + validation |
| Ollama not running | LLM call fails → exception → CLI shows error, API returns 500 |
| Model not found | `main.py` warns on startup: "Model not found in Ollama" |
| Validation fails | Specialist revises once, re-validated, delivered as-is if still failing |

### Thread Safety
| Action | Behavior |
|--------|----------|
| Concurrent API requests | SQLite write-lock prevents corruption |
| Multiple Streamlit sessions | Each has own session state |
| History DB locked | Waits and retries |

### Calculator Tool
| Input | Result |
|-------|--------|
| `2+2` | `4` |
| `10/3` | `3.333...` |
| `invalid syntax` | Error message (not crash) |
| Deeply nested (51+ levels) | Error: "Max nesting depth exceeded" |

---

## 7. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'config'` | `sys.path` missing | Already fixed in all entry points |
| Ollama connection refused | Ollama not installed/running | Install Ollama, or set `USE_DEMO_LLM=true` |
| Streamlit shows nothing | Port conflict | Kill other streamlit processes: `pkill streamlit` |
| History DB locked | Concurrent writes | Delete DB: `rm logs/history.db` |
| API returns 500 | LLM failure in non-demo mode | Set `USE_DEMO_LLM=true` in `.env` |
| `ollama pull` fails | No internet or disk space | Check connection, free space |
| No output from CLI | Permission or path issue | Run from project root directory |
| Tests fail | History DB from previous run | `rm -f logs/history.db && python3.12 -m pytest tests/ -v` |

---

## 8. Configuration Reference

`.env` file:
```ini
# Core switch
USE_DEMO_LLM=true           # true=demo mode (no LLM), false=real LLM

# LLM (only used when USE_DEMO_LLM=false)
LLM_PROVIDER=ollama          # ollama (free) or openai (paid)
LLM_MODEL=llama3.2:3b        # Ollama model name

# Limits
MAX_QUERY_LENGTH=2000        # Max input characters
MAX_REVISIONS=1              # Max validation retry attempts
MAX_HISTORY_LIMIT=100        # Max history entries stored
CALCULATOR_MAX_NESTING=50    # Max expression depth
```

---

## 9. Development Guide

### Adding a New Tool
1. Create file in `tools/` (e.g., `tools/slack.py`)
2. Create a `crewai.tools.BaseTool` subclass with `_run()` method
3. Import and add to `ROUTING_MAP` in `crews/support_crew.py`

### Adding a New Agent
1. Add config to `config/agents.yaml`
2. Create factory in `agents/` (e.g., `agents/shipping.py`)
3. Add task in `tasks/` (e.g., `tasks/shipping.py`)
4. Add entry to `ROUTING_MAP` in `crews/support_crew.py`

### Adding demo responses
Edit `tools/demo_llm.py`:
- Add keywords to `CLASSIFICATION_KEYWORDS`
- Add response text constants
- Add to `_handle_specialist()` method

### Running Tests
```bash
# All 77 tests
python3.12 -m pytest tests/ -v

# Single file
python3.12 -m pytest tests/test_tools.py -v

# With coverage
python3.12 -m pytest tests/ --cov=. --cov-report=term-missing
```

---

## 10. API Endpoint Deep Reference

### POST /chat — Process a query
```json
// Request
{"query": "I was charged twice", "conversation_id": ""}

// Response (200)
{
  "id": 1,
  "conversation_id": "conv_a1b2c3d4e5f6",
  "query": "I was charged twice",
  "classification": "billing",
  "tools_used": ["Currency Converter", "Company Data"],
  "routing_rationale": "billing: classified via keyword matching",
  "response": "Thank you for reaching out...",
  "validated": true,
  "validation_report": "APPROVED: Demo response meets quality criteria.",
  "execution_time": 0.01
}

// Error (422) — missing query
{"detail": [{"type": "missing", "loc": ["body", "query"], "msg": "field required"}]}

// Error (500) — LLM failure (non-demo mode)
{"detail": "Internal processing error"}
```

### GET /history — Paginated history
```json
// Response (200)
{
  "entries": [
    {
      "id": 1,
      "conversation_id": "conv_a1b2c3d4e5f6",
      "timestamp": "2026-07-30T14:00:00",
      "query": "I was charged twice",
      "classification": "billing",
      "tools_used": ["Currency Converter", "Company Data"],
      "response": "Thank you...",
      "validated": true,
      "execution_time": 0.01,
      "feedback": null
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### GET /stats — System statistics
```json
// Response (200)
{
  "total": 5,
  "classified": 4,
  "validated": 4,
  "avg_execution_time": 0.02,
  "by_category": {"billing": 2, "technical": 1, "sales": 1, "escalate": 1},
  "feedback_positive": 2,
  "feedback_negative": 0
}
```

### GET /export — Data export
```bash
# CSV format
curl "localhost:8000/export?format=csv" > history.csv

# JSON format
curl "localhost:8000/export?format=json" > history.json

# Filtered
curl "localhost:8000/export?format=csv&classification=billing"
curl "localhost:8000/export?format=json&conversation_id=conv_abc"
```

---

## 11. Project Roadmap

### Current Status (v1.1.0) ✅
- 5 agents, 6 tasks, 5 tools, 3 interfaces
- 77 tests passing, Docker, Makefile, documentation
- Demo mode works without any LLM
- Full API with 8 endpoints
- SQLite history with search, filter, export, feedback

### Next Steps (When Ready)
| Priority | Feature | Effort |
|----------|---------|--------|
| High | Real CRM integration (replace mock company_data.py) | 2-3 days |
| High | User authentication (API keys, sessions) | 1-2 days |
| Medium | SSE streaming for real-time responses | 1 day |
| Medium | File upload for screenshots | 1 day |
| Medium | Analytics dashboard (trends, response times) | 2 days |
| Low | CI/CD pipeline (GitHub Actions) | 0.5 day |
| Low | Multi-language i18n | 2 days |
| Low | Human escalation (Slack/email) | 2 days |

---

## 12. File-by-File Reference

| File | Lines | Purpose | Key Detail |
|------|-------|---------|------------|
| `main.py` | 121 | CLI entry | `--demo` sets USE_DEMO_LLM, checks Ollama, runs queries |
| `config/settings.py` | 26 | Configuration | 10 env vars + `get_llm()` |
| `config/agents.yaml` | 54 | Agent defs | Router, Billing, Technical, Sales, Validator |
| `config/tasks.yaml` | 96 | Task defs | Routing, Billing, Technical, Sales, Validation |
| `agents/router.py` | 29 | Router agent | Loads config from YAML, creates Agent with llm |
| `agents/billing.py` | 29 | Billing agent | Same pattern as router |
| `agents/technical.py` | 29 | Technical agent | Same pattern |
| `agents/sales.py` | 29 | Sales agent | Same pattern |
| `agents/validator.py` | 29 | Validator agent | Same pattern |
| `tasks/routing.py` | 25 | Routing task | Formats description with query |
| `tasks/billing.py` | 25 | Billing task | Same pattern |
| `tasks/technical.py` | 25 | Technical task | Same pattern |
| `tasks/sales.py` | 25 | Sales task | Same pattern |
| `tasks/validation.py` | 25 | Validation task | Formats with query + response |
| `crews/support_crew.py` | 234 | Pipeline | `run()` dispatches to `_run_demo()` or CrewAI pipeline |
| `tools/demo_llm.py` | 175 | Demo responses | Keyword classifier + 4 canned responses + DemoLLM class |
| `tools/calculator.py` | 69 | Calculator | AST evaluator with nesting limit |
| `tools/web_search.py` | 64 | Web search | DuckDuckGo, no API key |
| `tools/custom_api.py` | 74 | Weather+Currency | Open-Meteo + Frankfurter, both free |
| `tools/company_data.py` | 80 | Mock data | Customers, invoices, orders, products |
| `api/fastapi_app.py` | 254 | API server | 8 endpoints with Pydantic validation |
| `api/history_store.py` | 103 | SQLite store | Thread-safe, auto-migration |
| `ui/streamlit_app.py` | 402 | Web UI | CSS, chat, history, settings, feedback |
| `tests/` (5 files) | 550 | Test suite | 77 tests all passing |
| `FINAL_CONCLUSION.md` | — | Technical ref | Architecture, commands, verification |
| `PLAN.md` | — | This file | Complete plan with examples |

---

## 13. Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Points                             │
│                                                            │
│  main.py          streamlit_app.py     fastapi_app.py      │
│  (CLI)            (Web UI :8501)       (API :8000)         │
└────────┬──────────────────┬──────────────────┬──────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │    SupportCrew.run()    │
              │                         │
              │  USE_DEMO_LLM?          │
              │    YES → _run_demo()    │
              │    NO  → CrewAI agents  │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │     Result Dict         │
              │  + SQLite HistoryStore  │
              └────────────┬────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
         CLI print    Streamlit UI    API JSON
```

---

## 14. Expectation Checklist

Before using the system, verify:

- [ ] `pip install -r requirements.txt` completed
- [ ] `.env` exists (copy from `.env.example`)
- [ ] `USE_DEMO_LLM=true` (default, or `false` if Ollama is running)
- [ ] Running from project root directory
- [ ] Port 8501 (Streamlit) and 8000 (API) are free
- [ ] For real LLM: `ollama pull llama3.2:3b` done and Ollama is running
- [ ] `rm -f logs/history.db` if you want a fresh start
