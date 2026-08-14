#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Running Model × Prompt Evaluation Matrix ==="
uv run python evals/matrix_runner.py "$@"
