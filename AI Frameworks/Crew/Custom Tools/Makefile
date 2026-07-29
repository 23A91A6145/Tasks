.PHONY: install lint test test-all coverage clean build serve docker-build docker-run precommit

install:
	pip install -e ".[dev,api]"

lint:
	ruff check crew_tools/ tests/ --fix
	ruff format crew_tools/ tests/ --check

test:
	python -m pytest tests/ -x -q

test-all:
	python -m pytest tests/ -x -v

coverage:
	python -m pytest tests/ --cov=crew_tools --cov-report=term --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

clean:
	rm -rf build/ dist/ *.egg-info/ htmlcov/ .coverage
	rm -rf .mypy_cache .ruff_cache __pycache__ */__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build: clean
	python -m build

serve:
	crew-tools serve --reload

docker-build:
	docker build -t crew-tools .

docker-run:
	docker run -p 8000:8000 crew-tools

precommit:
	pre-commit run --all-files
