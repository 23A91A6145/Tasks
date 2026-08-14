#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Running Evaluation Suite ==="
uv run python evals/run_eval.py
