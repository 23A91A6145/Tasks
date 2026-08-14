#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Starting FastAPI Evaluation Service & Dashboard ==="
echo "Access Interactive Dashboard at: http://127.0.0.1:8000"
echo "Access OpenAPI Documentation at: http://127.0.0.1:8000/docs"
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
