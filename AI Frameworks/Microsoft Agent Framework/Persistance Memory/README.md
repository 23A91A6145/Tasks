# 🤖 Persistent-Memory Chat CLI (Complete Volumes 1-5)
> **Stateful AI Assistant powered by Microsoft Agent Framework Patterns (`AgentThread` + `FileHistoryProvider` + Semantic Fact Extractor + Memory Compactor + Fallback Circuit Breaker + Analytics Engine)**

[![Cost](https://img.shields.io/badge/Cost-100%25%20Free-brightgreen.svg)](#-cost--hardware-suitability)
[![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%7C%20Linux%20%7C%20Docker-blue.svg)](#-environment-setup)
[![Python](https://img.shields.io/badge/Python-3.9%2B-informational.svg)](#-environment-setup)
[![Volume](https://img.shields.io/badge/Volume-1--5%20Complete-brightgreen.svg)](#-project-roadmap-volume-1-to-5)
[![Tests](https://img.shields.io/badge/Tests-20%2F20%20Passed-success.svg)](#-7-running-automated-tests)

---

## 🎯 1. Project Overview & Aim

### ❓ What is Persistent Memory System?
Standard chatbots lose context as soon as you close the application. **Persistent Memory System** enables an AI assistant to save conversation sessions to disk, extract key user facts automatically, monitor token statistics, summarize long conversations into persistent memory blocks, handle network outages via Fallback Circuit Breakers, and reload past sessions seamlessly across application restarts.

```
Run 1 (Session: session_001)
  You > My name is Alice and I am a Lead AI Engineer.
  Assistant > Hello Alice! Saved name and role to persistent memory.
  (Application Exits)

Run 2 (Session: session_001)
  You > What do you know about me?
  Assistant > Persistent Memory Recall:
              - Name: Alice
              - Role: Lead AI Engineer
```

### 🎯 Aim
To build a production-ready, portfolio-quality stateful AI Chat CLI demonstrating state persistence, session metadata indexing, semantic user fact extraction, sliding window memory compaction, provider fallback circuit breakers, token analytics dashboards, multi-format history exports, and context sliding windows using Python and Rich terminal UI.

---

## 🏗️ 2. Core Concepts: Why AgentThread, FileHistoryProvider, MemoryCompactor & Fallback Circuit Breaker?

| Concept | Description | Why It Matters |
| :--- | :--- | :--- |
| **`FileHistoryProvider`** | Reads and appends message records into lightweight JSONL files (`history/session_001.jsonl`). | Guarantees atomic, append-only file persistence without needing external database servers. |
| **Session Index (`index.json`)** | Global session metadata registry storing custom titles, message counts, timestamps, extracted facts, and memory summaries. | Enables fast session listing and retrieval without scanning every file. |
| **Semantic Fact Extractor** | Parses user text turns and extracts key facts (Name, Role, Tech Stack, Location, Preferences). | Automatically persists user facts across restarts and injects them into System Prompts. |
| **`MemoryCompactor`** | Automatically summarizes older overflow messages when history exceeds sliding window limits. | Prevents token overflow while preserving deep historical memory across 100+ turns. |
| **Fallback Circuit Breaker** | Auto-detects API dropouts or missing keys and routes execution to the local offline Mock engine. | Guarantees 100% application uptime without crashes or unhandled exceptions. |
| **`AnalyticsEngine`** | Calculates token usage ratios, average tokens per turn, fact density, disk size, and system stats. | Provides production-ready observability into memory efficiency and cost tracking. |

---

## 🟢 3. Cost & Hardware Suitability

- **100% Free**: Operates offline with a zero-cost intelligent local engine (`LLM_PROVIDER=mock`).
- **Ollama Local LLM Support**: Connects seamlessly to Ollama (`llama3.1:8b` or `phi3`).
- **Free Cloud LLMs**: Option to connect to free tiers of Groq or Google Gemini API.
- **Laptop Friendly**: Minimal RAM/CPU footprint, zero background server required.

---

## 🗂️ 4. Project Structure

```
persistent-memory-chat-cli/
│
├── app/
│   ├── __init__.py      # Package initialization
│   ├── config.py        # Environment & App Config Loader
│   ├── utils.py         # Logger setup, token estimator, timestamps
│   ├── compaction.py    # Volume 4 MemoryCompactor (Sliding Window Summarizer)
│   ├── analytics.py     # Volume 3 AnalyticsEngine (Token & System Stats)
│   ├── history.py       # FileHistoryProvider + index.json tracking & memory summary
│   ├── memory.py        # PersistentMemoryManager + Semantic Fact Extractor + Summarizer
│   ├── thread.py        # AgentThread (system instructions + facts + summary context)
│   ├── agent.py         # ChatAgent (Volume 4 Fallback Circuit Breaker + latency tracking)
│   ├── commands.py      # Slash command dispatcher (/analytics, /export, /compact)
│   └── cli.py           # Rich Terminal UI Controller (Volume 4 Banner & Latency)
│
├── history/             # Session storage directory (.jsonl + index.json)
├── logs/                # Application logs (chat.log, error.log)
├── tests/               # Automated unit test suite (20 passing tests)
│   ├── test_config.py
│   ├── test_history.py
│   ├── test_agent.py
│   ├── test_volume2_features.py
│   ├── test_volume3_features.py
│   ├── test_volume4_features.py
│   └── test_volume5_deployment.py  # Deployment, Docker & Demo tests
│
├── docs/
│   └── architecture.md  # System Architecture Documentation (Volumes 1 - 5)
│
├── .env                 # Environment config
├── .env.example         # Template environment config
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker compose configuration
├── README.md            # Documentation
├── demo.py              # End-to-end automated demo & portfolio verification script
└── main.py              # Application entry point
```

---

## 💻 5. Environment Setup & Execution Guide

### Step 1: Install System Prerequisites (Ubuntu/Linux)
```bash
sudo apt update
sudo apt install -y python3 python3-venv git
```

### Step 2: Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
```

### Step 5: Run Automated System Demo
```bash
python demo.py
```

### Step 6: Launch the Interactive Chat CLI
```bash
python main.py
```

---

## ⌨️ 6. Available Slash Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `/help` | Displays available commands & usage guide | `/help` |
| `/history [user\|assistant]` | Displays persistent conversation history (optionally filtered by role) | `/history user` |
| `/facts` | Displays extracted semantic user facts stored in memory | `/facts` |
| `/search <query>`| Searches message history for matching keyword | `/search python` |
| `/stats` or `/analytics` | Displays Token Usage Dashboard & System Overview | `/analytics` |
| `/title [name]` | Views or renames active session title | `/title Production Architecture` |
| `/compact` | Compacts and repairs JSONL storage file | `/compact` |
| `/session [id]`| Lists active sessions or switches to session ID | `/session session_002` |
| `/new [id]` | Alias for switching/creating a session | `/new dev_session` |
| `/clear` | Clears memory history for active session | `/clear` |
| `/model [name]`| Shows or switches LLM provider (`mock`, `ollama`, `groq`, `gemini`) | `/model mock` |
| `/export [txt\|md\|json]` | Exports session history into TXT, Markdown, or JSON format | `/export md` |
| `/exit` | Exits the application cleanly | `/exit` |

---

## 🧪 7. Running Automated Tests

Run unit tests to verify configuration, persistent memory storage, session indexing, fact extraction, history search, analytics, multi-format export, memory compactor, fallback circuit breaker, latency tracking, and docker deployment:

```bash
.venv/bin/pytest tests/ -v
```

---

## 🐳 8. Docker Deployment

### Run using Docker Compose
```bash
docker-compose up --build -d
docker attach persistent_chat_cli
```

---

## 📈 9. Project Roadmap (Volumes 1 to 5 - COMPLETE)

- [x] **Volume 1: Foundation** (Architecture, Environment, FileHistoryProvider, AgentThread, Rich UI, Mock Provider)
- [x] **Volume 2: Persistent Memory System** (Session Indexing, Semantic Fact Extractor, Keyword Search, Compaction, Fact Injection)
- [x] **Volume 3: Professional Features** (Token Analytics Dashboard, Multi-Format Exporter [TXT, MD, JSON], Role Filtering, Latency Badges)
- [x] **Volume 4: Production Features** (Memory Compactor, Sliding Window Summarization, Provider Fallback Circuit Breaker, Error Recovery)
- [x] **Volume 5: Deployment & Portfolio** (Docker Packaging, End-to-End Demo Script, Complete Portfolio Showcase Documentation)
