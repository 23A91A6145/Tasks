# Use Python 3.12 slim image for a lightweight production container
FROM python:3.12-slim

# Set environment variables (overridable at runtime via docker-compose)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0
ENV LLM_PROVIDER=mock

# Set workspace directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ app/
COPY templates/ templates/
COPY main.py .
COPY run_demo.py .

# Expose server port
EXPOSE 8000

# Healthcheck: report unhealthy if the API stops responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fs http://127.0.0.1:8000/api/health || exit 1

# Run the FastAPI application using uvicorn
CMD ["python", "main.py"]
