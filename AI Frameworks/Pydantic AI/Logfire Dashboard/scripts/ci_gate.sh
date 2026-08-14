#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Running CI/CD Automated Quality Gate ==="
uv run python evals/ci_gate.py "$@"
