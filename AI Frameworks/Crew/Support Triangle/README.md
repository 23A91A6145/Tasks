# AI Support Triage Crew

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![CrewAI](https://img.shields.io/badge/built%20with-CrewAI-6C5CE7)](https://crewai.com)
[![Tests](https://img.shields.io/badge/tests-77%20passing-brightgreen)](PLAN.md#9-development-guide)
[![Demo](https://img.shields.io/badge/demo-no%20LLM%20needed-orange)](PLAN.md#1-what-this-is)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Multi-agent AI customer support triage: classify → route → specialize → validate → deliver.

**Zero cost.** No API keys. No cloud. Runs locally on Ollama or in demo mode with no LLM at all.

---

## Quick Start

```bash
cd /home/cherry/Desktop/1_Gen/Tasks/Crew/Support Triangle
pip install -r requirements.txt

# Demo mode (no LLM needed — works right now):
python main.py --demo
streamlit run ui/streamlit_app.py
uvicorn api.fastapi_app:app --port 8000
```

## 3 Interfaces

| Interface | Command | URL |
|-----------|---------|-----|
| CLI | `python main.py "your query"` | Terminal |
| Web UI | `streamlit run ui/streamlit_app.py` | http://localhost:8501 |
| API | `uvicorn api.fastapi_app:app --port 8000` | http://localhost:8000/docs |

## Stats

- **47 files**, 2,243 LOC Python, 77 tests
- **5 agents** (Router, Billing, Technical, Sales, Validator)
- **5 tools** (Web Search, Calculator, Weather, Currency, Company Data)
- **8 API endpoints** (health, chat, history, feedback, export, stats, delete)
- **$0 cost** — Ollama + DuckDuckGo + Open-Meteo + Frankfurter

---

## Full Plan

See **[PLAN.md](PLAN.md)** for complete walkthroughs, API examples, troubleshooting, architecture, and everything else.
