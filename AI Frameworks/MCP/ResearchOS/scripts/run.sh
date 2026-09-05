#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "=========================================================="
echo "    🧠 Starting ResearchOS (Backend + Frontend)          "
echo "=========================================================="

# 1. Activate virtual environment
source .venv/bin/activate

# 2. Check if .env exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[+] Created .env from .env.example"
fi

# 3. Start Backend in background
echo "[+] Starting FastAPI backend on http://localhost:8000..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Trap signals to clean up background processes
trap "echo '[!] Stopping ResearchOS...'; kill $BACKEND_PID 2>/dev/null; exit" SIGINT SIGTERM EXIT

# 4. Wait for backend to be ready
echo "[+] Waiting for backend health check..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "[✓] Backend is healthy!"
        break
    fi
    sleep 0.5
done

# 5. Start Frontend
echo "[+] Starting React Frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================================="
echo "  🚀 ResearchOS is running!"
echo "  - Frontend UI:  http://localhost:5173"
echo "  - Backend API:  http://localhost:8000"
echo "  - Swagger Docs: http://localhost:8000/docs"
echo "=========================================================="
echo "  Press Ctrl+C to terminate all services."
echo ""

wait $BACKEND_PID $FRONTEND_PID
