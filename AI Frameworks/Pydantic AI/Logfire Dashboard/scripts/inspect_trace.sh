#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Trace-to-Failure Deep-Dive Inspector ==="
uv run python evals/trace_debugger.py "$@"
