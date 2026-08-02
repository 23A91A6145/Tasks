#!/usr/bin/env bash
# Dev runner: backend (8000) + frontend (3000) together.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() { kill 0 2>/dev/null || true; }
trap cleanup EXIT INT TERM

VENV=".venv"
if [ -d "$ROOT/apps/backend/.venv312" ]; then
  VENV=".venv312"
fi

echo "→ Starting backend  http://localhost:8000 (docs: /docs)  [venv: $VENV]"
(cd "$ROOT/apps/backend" && exec "$VENV/bin/uvicorn" app.main:app --reload --port 8000) &

echo "→ Starting frontend http://localhost:3000"
(cd "$ROOT/apps/frontend" && exec npm run dev) &

wait
