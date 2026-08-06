#!/bin/bash
# Set PYTHONPATH to project root and run uvicorn server
echo "============================================================"
echo " Starting Multi-Source Skills Hub on http://localhost:8000"
echo "============================================================"
export PYTHONPATH=.
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
