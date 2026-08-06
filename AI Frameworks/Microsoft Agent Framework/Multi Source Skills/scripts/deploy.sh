#!/bin/bash
# Docker build and run script
echo "============================================================"
echo " Packaging Skills Provider in Docker (16GB spec optimize)"
echo "============================================================"

# Build image
docker build -t skills-provider:latest .

echo ""
echo "============================================================"
echo " Starting Container on http://localhost:8000"
echo "============================================================"

# Ensure logs dir exists for mounting
mkdir -p logs

# Run container mapping port 8000 and mounting logs folder
docker run -d \
  --name skills-hub-container \
  -p 8000:8000 \
  -v "$(pwd)/logs:/workspace/logs" \
  --rm \
  skills-provider:latest

echo "Container launched in background."
echo "Use 'docker logs -f skills-hub-container' to tail logs."
echo "Use 'docker stop skills-hub-container' to terminate the app."
