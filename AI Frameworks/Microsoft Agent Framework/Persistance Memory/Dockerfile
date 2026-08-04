# Dockerfile for Persistent Memory Chat CLI
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Set default env
ENV LLM_PROVIDER=mock
ENV HISTORY_DIR=history
ENV LOGS_DIR=logs

# Run application interactive shell
CMD ["python", "main.py"]
