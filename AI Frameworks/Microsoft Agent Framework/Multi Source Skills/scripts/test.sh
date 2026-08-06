#!/bin/bash
# Set PYTHONPATH and run test suite
echo "============================================================"
echo " Running Multi-Source Skills Provider Pytest Suite"
echo "============================================================"
export PYTHONPATH=.
./.venv/bin/pytest -v
