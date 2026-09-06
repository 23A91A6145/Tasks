# Multi-stage Dockerfile: Frontend Build + Python Backend
FROM node:24-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS final
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic pydantic-settings aiosqlite httpx pyyaml sse-starlette

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY docs/ ./docs/

ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
