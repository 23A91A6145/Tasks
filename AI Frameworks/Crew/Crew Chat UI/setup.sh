#!/usr/bin/env bash
set -euo pipefail

echo "╔═══════════════════════════════════════════╗"
echo "║   Crew Chat UI — Automated Setup          ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# ─── Check Python ────────────────────────────────────────────
echo "🔍 Checking Python..."
PYTHON=""
for cmd in python3.12 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python not found. Install Python 3.10+ first."
    exit 1
fi

PY_VER=$($PYTHON --version 2>&1 | grep -oP '\d+\.\d+')
echo "   Found Python $PY_VER ($PYTHON)"
echo ""

# ─── Check / Install Ollama ─────────────────────────────────
echo "🔍 Checking Ollama..."
if command -v ollama &>/dev/null; then
    echo "   Ollama found: $(ollama --version 2>&1 | head -1)"

    if ollama list 2>/dev/null | grep -q llama; then
        echo "   ✅ Models already pulled"
    else
        echo "   📥 Pulling recommended model (llama3.2:3b)..."
        ollama pull llama3.2:3b
    fi
else
    echo "   ⚠️  Ollama not found."
    echo "   Install it manually: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   Then run: ollama pull llama3.2:3b"
    echo ""
    echo "   The app will run in fallback mode without Ollama."
fi
echo ""

# ─── Virtual Environment ────────────────────────────────────
echo "🔧 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
    echo "   Created .venv"
fi

source .venv/bin/activate
echo "   Activated virtual environment"
echo ""

# ─── Install Dependencies ───────────────────────────────────
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   Done!"
echo ""

# ─── Environment File ───────────────────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created .env from .env.example"
else
    echo "📝 .env already exists, skipping"
fi
echo ""

# ─── Run Tests ──────────────────────────────────────────────
echo "🧪 Running tests..."
$PYTHON -m pytest tests/ -q --tb=line 2>&1 | tail -3
echo ""

# ─── Launch ─────────────────────────────────────────────────
echo "╔═══════════════════════════════════════════╗"
echo "║   ✅ Setup Complete!                       ║"
echo "║                                           ║"
echo "║   Run:  source .venv/bin/activate         ║"
echo "║         streamlit run app.py              ║"
echo "║                                           ║"
echo "║   Or:  streamlit run app.py               ║"
echo "╚═══════════════════════════════════════════╝"
