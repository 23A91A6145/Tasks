.PHONY: install run test demo docker-up docker-down clean lint

install:
	python -m pip install -r requirements.txt

run:
	python main.py

test:
	python -m pytest -q

demo:
	python run_demo.py

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	rm -rf .pytest_cache **/__pycache__
	find checkpoints logs -name '*.json' -not -name 'approvals_db.json' -delete

lint:
	python -m pip show ruff >/dev/null 2>&1 && ruff check app tests main.py || echo "ruff not installed (optional)"
