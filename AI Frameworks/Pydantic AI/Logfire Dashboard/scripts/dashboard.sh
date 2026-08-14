#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Launching Observability Dashboard ==="
uv run python evals/dashboard.py
