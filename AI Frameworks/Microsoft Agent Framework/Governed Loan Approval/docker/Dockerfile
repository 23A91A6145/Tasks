# Stage 1: Build Frontend
FROM node:24-alpine AS frontend-builder
WORKDIR /app/web
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Copy built frontend assets from Stage 1 into the backend static folder
COPY --from=frontend-builder /app/api/static /app/apps/api/static/

EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
