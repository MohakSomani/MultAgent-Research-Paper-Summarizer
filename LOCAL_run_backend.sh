#!/bin/bash
set -e

# Script to run the MultAgent Research Paper Summarizer backend locally

# Activate virtual environment from backend folder
source backend/.venv/bin/activate

# Check if model exists
MODEL_PATH="backend/models/llama-2-7b.Q4_K_M.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model not found at $MODEL_PATH"
    echo "Please run ./LOCAL_setup.sh first to download the model"
    exit 1
fi

# Configure GPU settings if available
if command -v nvidia-smi &> /dev/null; then
    echo "🖥️ NVIDIA GPU detected, using GPU acceleration"
    export GPU_LAYERS=32
    export CUDA_VISIBLE_DEVICES=0
    # Fix CUDA memory issues
    export GGML_CUDA_NO_PINNED=1
    export GGML_CUDA_FORCE_MMQ=1
    export GGML_TENSOR_SPLIT_STRATEGY=2
else
    echo "⚠️ No GPU detected, running on CPU only"
    export GPU_LAYERS=0
fi

# Set model path
export MODEL_PATH="$MODEL_PATH"

echo "🚀 Starting backend server..."
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# In case the server crashes, don't close the terminal immediately
echo "⚠️ Server stopped. Press Enter to exit."
read
