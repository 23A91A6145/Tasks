# Crew Assistant — Runbook

## Quick Start

```bash
# 1. Install Ollama (free, local)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull a model
ollama pull llama3.2:3b

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py

# 5. Open in browser
# http://localhost:8501
```

## Commands

| Command | Description |
|---------|-------------|
| `streamlit run app.py` | Start the chat UI |
| `python -m pytest tests/ -q` | Run all tests |
| `ollama pull llama3.2:3b` | Download a free local model |
| `ollama list` | See available models |
| `ollama serve` | Start Ollama server manually |

## Directory Structure

```
Crew Chat UI/
├── app.py                  # Main entry point
├── crew/
│   ├── config.py           # Settings & env vars
│   ├── agents.py           # AI agent definitions
│   ├── tasks.py            # Task definitions
│   └── crew.py             # Crew orchestration
├── services/
│   ├── history.py          # Chat session persistence
│   ├── memory.py           # Conversation memory
│   ├── logger.py           # Logging setup
│   ├── validator.py        # Input validation
│   ├── model_service.py    # Model detection
│   └── mock_responder.py   # Fallback responses
├── ui/
│   ├── theme.py            # CSS design system
│   ├── chat.py             # Message rendering
│   ├── components.py       # UI components
│   ├── sidebar.py          # Sidebar panels
│   └── session_manager.py  # Session management
├── tests/                  # Test suite
├── .env                    # Environment config
└── requirements.txt        # Python dependencies
```

## Modes

- **Live Mode**: Ollama running with models → full AI responses
- **Fallback Mode**: No working LLM → intelligent template responses
- **Demo Mode**: No LLM at all → mock responses with full UI

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL_NAME` | `llama3.2:3b` | Ollama model to use |
| `CREW_TIMEOUT` | `120` | Request timeout in seconds |
| `MAX_QUERY_LENGTH` | `10000` | Max input characters |
| `MAX_TOKENS` | `2048` | Max response tokens |
| `LOG_LEVEL` | `INFO` | Logging level |
