# Multi-stage Docker build for clean, small production containers
FROM python:3.12-slim AS builder

WORKDIR /workspace

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list
COPY requirements.txt .

# Install dependencies into a separate wheels dir or folder
RUN pip install --no-cache-dir --user -r requirements.txt


# Runner stage
FROM python:3.12-slim AS runner

WORKDIR /workspace

# Copy local dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/workspace

# Copy codebase
COPY . .

# Expose port and declare volume for persistent database logs
EXPOSE 8000
VOLUME ["/workspace/logs"]

# Launch dashboard server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
