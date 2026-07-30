<div align="center">
  <img src="assets/banner.png" alt="Crew Chat UI" width="600"/>
  <h1>🤖 Crew Chat UI</h1>
  <p><strong>Production-grade multi-agent AI chat — 100% free with Ollama</strong></p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-use-cases">Use Cases</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-project-structure">Structure</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.12-bcd /home/cherry/Desktop/1_Gen/Tasks/Crew/Crew\ Chat\ UI
streamlit run app.py
lue?logo=python"/>
    <img src="https://img.shields.io/badge/license-MIT-green"/>
    <img src="https://img.shields.io/badge/tests-87%20passing-brightgreen"/>
    <img src="https://img.shields.io/badge/version-5.0.0-orange"/>
  </p>
</div>

---

## ✨ Features

### 🤖 Multi-Agent AI Pipeline
```
User Query → 🔍 Research Agent → 📊 Analysis Agent → ✍️ Writer Agent → Response
```
Three specialized CrewAI agents working in sequence for comprehensive answers.

### 🎨 Professional UI
- **Glassmorphism design** with gradient bubbles, shadows, animations
- **Dark/Light theme** toggle in sidebar
- **Animated message entry** with slide-in and hover effects
- **Markdown rendering** — code blocks, tables, blockquotes, images
- **Responsive** — desktop, tablet, mobile (3 breakpoints)

### ⚙ Production-Grade
| Feature | Description |
|---------|-------------|
| Input Validation | XSS sanitization, length limits (10K chars) |
| Token Counter | Real-time token estimation per message + session |
| Message Search | Full-text search with yellow highlight |
| Provider Selector | Switch Ollama / OpenAI / OpenRouter in UI |
| System Prompt Editor | Custom agent instructions |
| Session Management | Save, load, delete conversations |
| Enhanced Export | Markdown + JSON download |
| Keyboard Shortcuts | Ctrl+Enter send, Escape clear, Ctrl+K search |
| Fallback Mode | Smart template responses when LLM unavailable |
| Rotating Logs | 5MB max, 3 backups |
| Request Timeout | Configurable (default 120s) |

### 🆓 100% Free
- **Ollama** — Local, no API key, runs on CPU/GPU
- **OpenRouter** — Free tier available
- **Mock Fallback** — Works even without any LLM

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.ai) for local AI

### One-Command Setup
```bash
curl -fsSL https://ollama.ai/install.sh | sh  # Install Ollama
ollama pull llama3.2:3b                         # Pull a free model
```

### Clone & Run
```bash
git clone https://github.com/yourusername/crew-chat-ui
cd crew-chat-ui

cp .env.example .env           # Ollama is default — no changes needed
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

### Verify Installation
```bash
python -m pytest tests/ -q     # 87 tests should pass
```

---

## 💡 Use Cases

| Use Case | How | Example Query |
|----------|-----|---------------|
| **Research** | Agent gathers & organizes information | _"Explain quantum computing"_ |
| **Code Review** | Agent analyzes code for bugs/style | _"Review this Python function..."_ |
| **Content Writing** | Agent drafts structured content | _"Write a blog post about AI ethics"_ |
| **Brainstorming** | Agent generates creative ideas | _"Brainstorm marketing strategies"_ |
| **Debugging** | Agent identifies & explains fixes | _"Why is this SQL query slow?"_ |
| **Learning** | Agent explains concepts simply | _"Explain the CAP theorem"_ |
| **Translation** | Agent translates with context | _"Translate this to Spanish"_ |
| **Analysis** | Agent extracts insights from data | _"Compare REST vs GraphQL"_ |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI                       │
│  ┌──────────┐  ┌─────────┐  ┌──────┐  ┌────────┐  │
│  │ Chat     │  │ Sidebar │  │Search│  │Export  │  │
│  │ Messages │  │ Config  │  │ Bar  │  │ MD/JSON│  │
│  └────┬─────┘  └─────────┘  └──────┘  └────────┘  │
└───────┼─────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────┐
│              Crew Assistant (crew.py)                │
│  ┌─────────────────┐  ┌────────────┐  ┌─────────┐  │
│  │ 🔍 Research     │→│ 📊 Analysis │→│ ✍️ Writer │  │
│  │ Specialist      │  │ Expert     │  │ Response │  │
│  └────────┬────────┘  └────────────┘  └─────────┘  │
└───────────┼─────────────────────────────────────────┘
            │
     ┌──────▼──────┐     ┌──────────────┐
     │   Ollama    │     │   Fallback   │
     │ (local/free)│ or  │   Responder  │
     └─────────────┘     └──────────────┘
```

---

## 📁 Project Structure

```
crew-chat-ui/
├── app.py                  # Main entry point — Streamlit app
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project metadata
├── setup.sh                # One-command setup script
├── RUNBOOK.md              # Detailed run instructions
├── FINAL_CONCLUSION.md     # Full project documentation
│
├── crew/                   # CrewAI orchestration
│   ├── config.py           # Auto-detect provider, settings
│   ├── agents.py           # 3 agents with singleton pattern
│   ├── tasks.py            # Sequential task definitions
│   └── crew.py             # CrewAssistant + metrics + fallback
│
├── services/               # Backend services
│   ├── logger.py           # Rotating file + stdout logger
│   ├── memory.py           # Conversation memory (20-turn)
│   ├── history.py          # Session persistence (JSON)
│   ├── validator.py        # Input sanitization + validation
│   ├── mock_responder.py   # Smart fallback responses
│   ├── model_service.py    # Ollama model detection
│   ├── provider_service.py # Multi-provider switching
│   └── token_counter.py    # Token estimation
│
├── ui/                     # Streamlit UI components
│   ├── theme.py            # CSS design system (light/dark)
│   ├── chat.py             # Message rendering + search highlight
│   ├── components.py       # Input, search, export, controls
│   ├── sidebar.py          # Config, provider, agent info
│   └── session_manager.py  # Session CRUD
│
├── tests/                  # Test suite
│   ├── test_crew.py        # Backend tests
│   ├── test_ui.py          # UI + theme tests
│   └── test_volume5.py     # Volume 5 feature tests
│
├── logs/                   # Application logs
└── data/                   # Session storage
```

---

## 📊 Test Suite

```bash
# Run all 87 tests
python -m pytest tests/ -q

# With coverage
python -m pytest tests/ --cov=. -q

# Verbose
python -m pytest tests/ -v
```

---

## 🛠 Tech Stack

| Component | Technology | Cost |
|-----------|------------|------|
| UI Framework | [Streamlit](https://streamlit.io) | Free |
| AI Agents | [CrewAI](https://crewai.com) | Free |
| LLM (default) | [Ollama](https://ollama.ai) + llama3.2 | Free |
| LLM (alt) | OpenAI / OpenRouter | Free tier / Paid |
| Storage | JSON filesystem | Free |
| Logging | Python logging + RotatingFileHandler | Free |
| Python | 3.12+ | Free |

---

## 📜 License

MIT — Free for all use.

---

## 🤝 Contributing

Issues, PRs, and feedback welcome. This project is designed to be:
- **Free** — No paid dependencies
- **Local** — Runs on your laptop
- **Modular** — Easy to extend
- **Production-ready** — Validated, tested, documented
