#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "================================================================="
echo "   🧠 ResearchOS — Production Agentic AI Research Platform       "
echo "================================================================="

# 1. Environment Setup Check
if [ ! -d ".venv" ]; then
    echo "[*] Virtual environment not detected. Running setup..."
    ./scripts/setup.sh
fi

source .venv/bin/activate

# 2. Build Frontend if dist is missing
if [ ! -d "frontend/dist" ]; then
    echo "[*] Building frontend assets..."
    cd frontend && npm install && npm run build && cd ..
fi

# 3. Open browser automatically in background after 2 seconds
(sleep 2 && (xdg-open http://localhost:8000 2>/dev/null || sensible-browser http://localhost:8000 2>/dev/null || python3 -m webbrowser http://localhost:8000 2>/dev/null || true)) &

echo ""
echo "================================================================="
echo "   🚀 Application Ready!"
echo "   👉 Research Workspace UI: http://localhost:8000"
echo "   👉 Interactive API Docs:   http://localhost:8000/docs"
echo "   👉 System Health Check:     http://localhost:8000/health"
echo "================================================================="
echo "   Starting Uvicorn Server (Press Ctrl+C to terminate)..."
echo ""

exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
