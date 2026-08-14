.PHONY: install test test-v1 inspect review clean help

VENV = .venv
PYTHON = $(VENV)/bin/python
PYTEST = $(VENV)/bin/pytest

help:
	@echo "🛡️ DeepRepo Reviewer - Volume 1 Automation Commands"
	@echo "================================================="
	@echo "make install      : Install dependencies into virtualenv"
	@echo "make test         : Run all test suites (unit, agent, integration)"
	@echo "make inspect      : Inspect current repository profile"
	@echo "make plan         : Generate autonomous review plan"
	@echo "make review       : Execute autonomous review on codebase"
	@echo "make clean-fixture: Run review against fixtures/clean"
	@echo "make vuln-fixture : Run review against fixtures/vulnerable"
	@echo "make clean        : Remove temporary test caches and reports"

install:
	uv pip install -e ".[dev]"

test:
	$(PYTEST) -v

test-v1:
	$(PYTEST) tests/agent tests/integration -v

inspect:
	$(PYTHON) -m app.cli inspect .

plan:
	$(PYTHON) -m app.cli plan .

review:
	$(PYTHON) -m app.cli review .

clean-fixture:
	$(PYTHON) -m app.cli review fixtures/clean

vuln-fixture:
	$(PYTHON) -m app.cli review fixtures/vulnerable

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ reports/rev-*.md reports/rev-*.json
