#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Running Targeted Regression & Safety Suite ==="
uv run python evals/run_eval.py --category safety
uv run python evals/run_eval.py --category boundary
