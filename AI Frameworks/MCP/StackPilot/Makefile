.PHONY: help install test eval backend frontend run clean

help:
	@echo "StackPilot Automation Commands:"
	@echo "  make install    - Set up virtualenv and install all python + frontend dependencies"
	@echo "  make test       - Run all backend unit, agent, and integration tests"
	@echo "  make eval       - Run migration benchmark evaluation harness"
	@echo "  make backend    - Start FastAPI backend server on port 8000"
	@echo "  make frontend   - Start Vite frontend dev server on port 5173"
	@echo "  make build      - Compile production frontend build"
	@echo "  make clean      - Clean temporary files and caches"

install:
	uv venv --python /usr/bin/python3.12 .venv
	uv pip install fastapi "uvicorn[standard]" langgraph langchain-core langchain-ollama pydantic pydantic-settings httpx aiosqlite pytest pytest-asyncio python-dotenv
	cd frontend && npm install

test:
	.venv/bin/pytest backend/tests/ -v

eval:
	.venv/bin/python3 evals/evaluators/run_benchmark.py

backend:
	.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

clean:
	rm -rf .pytest_cache frontend/dist __pycache__ backend/app/**/__pycache__
