#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Side-by-Side Experiment Comparison ==="
uv run python evals/compare.py "$@"
