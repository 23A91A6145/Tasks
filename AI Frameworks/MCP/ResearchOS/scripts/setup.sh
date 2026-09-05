#!/usr/bin/env bash
set -e

echo "=== Setting up ResearchOS Ubuntu Environment ==="
uv venv
source .venv/bin/activate
uv pip install -e .

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

echo "=== Setup Complete! Run './scripts/dev.sh' to start ==="
