.PHONY: install run demo ui api test test-quiet clean docker

install:
	pip install -r requirements.txt

run:
	python main.py "$(filter-out $@,$(MAKECMDGOALS))"

demo:
	python main.py --demo

ui:
	streamlit run ui/streamlit_app.py

api:
	uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000

test:
	python -m pytest tests/ -v --tb=short

test-quiet:
	python -m pytest tests/ --tb=short -q

docker:
	docker-compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -f logs/*.db logs/*.log logs/*.json
