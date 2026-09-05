.PHONY: run dev test test-unit build clean docker-up docker-down

run:
	./run.sh

dev:
	./scripts/dev.sh

test:
	./scripts/test.sh

build:
	cd frontend && npm run build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf __pycache__ .pytest_cache
