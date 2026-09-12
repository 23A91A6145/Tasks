#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================="
echo "🚀 Launching Hashira ATS Platform"
echo "=================================================="

# 1. Check Virtual Environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv --python python3.12 --system-site-packages .venv
fi

source .venv/bin/activate

# 2. Verify Streamlit Executable in .venv
if [ ! -f ".venv/bin/streamlit" ]; then
    echo "Setting up Streamlit launcher..."
    cat << 'PYEOF' > .venv/bin/streamlit
#!/home/cherry/hashira/.venv/bin/python
import re
import sys
from streamlit.web.cli import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
PYEOF
    chmod +x .venv/bin/streamlit
fi

# 3. Clean port 8501 if previously occupied
if command -v fuser >/dev/null 2>&1; then
    fuser -k 8501/tcp 2>/dev/null || true
fi

echo "✓ Environment validated."
echo "✓ Launching Streamlit interface on port 8501..."
echo "👉 Open your browser at: http://localhost:8501"
echo "=================================================="

exec .venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
