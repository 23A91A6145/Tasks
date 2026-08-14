#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Ingesting Production Failure Feedback ==="
uv run python evals/production_feedback.py "$@"
