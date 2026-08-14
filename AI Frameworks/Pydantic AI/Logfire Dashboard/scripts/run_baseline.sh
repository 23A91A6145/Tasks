#!/usr/bin/env bash
set -e

echo "=== [AgentEval Lab] Running Baseline Experiment ==="
export AGENT_MODEL="test"
export MIN_PASS_RATE="0.85"
uv run python evals/run_eval.py
