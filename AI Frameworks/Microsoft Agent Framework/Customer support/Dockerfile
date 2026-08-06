FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies (including git for git installs if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app /workspace/app
COPY .env /workspace/.env

# Create data directories
RUN mkdir -p /workspace/history /workspace/logs

EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
