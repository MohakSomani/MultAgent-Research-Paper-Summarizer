#!/bin/bash

set -e

# Function to check if nvidia-smi is available
check_gpu() {
  if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    return 0
  else
    echo "⚠️ No NVIDIA GPU detected, will run on CPU only"
    export GPU_LAYERS=0
    return 1
  fi
}

# Create models directory for volume mounting
mkdir -p models

# Check for GPU
check_gpu

# Stop and remove existing containers
echo "🧹 Cleaning up existing containers..."
docker compose down

# Remove existing images
echo "🧹 Removing existing images..."
docker rmi $(docker images -q 'multagent-research-paper-summarizer_*') --force 2>/dev/null || true

# Build and start containers
echo "🚀 Starting the application..."
echo "📝 The model will be downloaded inside the container if needed..."
docker compose up --build -d

echo "✅ Application is running!"
echo "📊 Backend API: http://localhost:8000"
echo "🖥️ Frontend: http://localhost:5173"

# Show logs
echo "📝 Showing logs (Ctrl+C to exit):"
docker compose logs -f