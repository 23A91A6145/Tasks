#!/usr/bin/env bash
# OPTIONAL: enable the full CrewAI hierarchical crew.
#
# The base setup works with ZERO dependencies beyond the standard stack
# (rule-engine fallback). This script adds CrewAI in a separate
# Python 3.12 venv, which requires the OPENAI_API_KEY (or an
# OpenAI-compatible base URL) in apps/backend/.env to be used.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PY312="$(command -v python3.12 || true)"
if [ -z "$PY312" ]; then
  echo "✗ python3.12 not found. CrewAI requires Python ≤3.13."
  echo "  Install Python 3.12 first, then re-run this script."
  exit 1
fi

echo "→ Creating Python 3.12 venv (.venv312)"
cd "$ROOT/apps/backend"
"$PY312" -m venv .venv312
.venv312/bin/pip install --upgrade pip
.venv312/bin/pip install -r requirements-ai.txt
.venv312/bin/pip install -r requirements.txt

echo ""
echo "✅ CrewAI installed."
echo "   Next: add your LLM key to apps/backend/.env, e.g."
echo "   OPENAI_API_KEY=sk-...  (or set an OpenAI-compatible base URL)"
echo "   Then run:  bash scripts/dev.sh"
echo "   The engine will auto-select 'crewai' when a key is present."
