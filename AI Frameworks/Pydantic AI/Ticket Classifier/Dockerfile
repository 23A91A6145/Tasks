# Use a slim Python base image
FROM python:3.12-slim AS builder

# Install uv for rapid dependency resolution and isolation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Sync dependencies (creates a local .venv)
RUN uv sync --frozen --no-dev

# Final Stage
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv
# Copy application code
COPY app/ /app/app/
COPY main.py /app/
COPY README.md /app/

# Environment configurations
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000
ENV HOST=0.0.0.0
ENV DATABASE_PATH="/app/tickets.db"
ENV ENV=production
ENV DEBUG=false

# Expose port
EXPOSE 8000

# Run schema initialization then launch FastAPI server
CMD ["python", "main.py", "server", "--host", "0.0.0.0", "--port", "8000", "--no-reload"]
