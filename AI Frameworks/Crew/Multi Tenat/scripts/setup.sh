#!/usr/bin/env bash
# One-time setup: Python venv + backend deps + frontend deps.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "→ Backend (Python venv + deps)"
cd "$ROOT/apps/backend"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements-dev.txt
[ -f .env ] || cp .env.example .env

echo "→ Frontend (npm)"
cd "$ROOT/apps/frontend"
npm install
[ -f .env ] || cp .env.example .env

echo ""
echo "✅ Setup complete. Run with:  bash scripts/dev.sh"
echo "   Backend API docs:  http://localhost:8000/docs"
echo "   Frontend:          http://localhost:3000"
