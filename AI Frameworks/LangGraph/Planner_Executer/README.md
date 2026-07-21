# 🤖 Two-Agent Planner + Executor

AI system with **Groq** (planner) + **Ollama** (executor) + auto-replanning on failure.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn api.app:app --reload --port 8000

# Run Streamlit UI (separate terminal)
streamlit run ui/streamlit_app.py
```

Open **http://localhost:8501** for the UI or **http://localhost:8000/docs** for API docs.

## Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/plan` | Generate plan only |
| POST | `/api/execute` | Execute given steps |
| POST | `/api/run` | Full pipeline (async) |
| GET | `/api/status/{id}` | Job status |
| GET | `/api/logs/{id}` | Step results |

## Architecture

```
User → Streamlit (:8501) → FastAPI (:8000)
                              ↓
                    Planner (Groq/LLaMA 3.3 70B)
                              ↓
                    Parser → Executor (Ollama/LLaMA 3.2 3B)
                              ↓
                    Replanner (Groq, on failure)
```

## Models

| Agent | Provider | Model |
|-------|----------|-------|
| Planner | Groq | `llama-3.3-70b-versatile` |
| Executor | Ollama | `llama3.2:3b` |
| Replanner | Groq | `llama-3.3-70b-versatile` |
