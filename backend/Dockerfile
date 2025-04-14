FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including CUDA tools
RUN apt-get update && \
    apt-get install -y git curl build-essential cmake && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Set pip cache directory
ENV PIP_CACHE_DIR=/root/.cache/pip

# Copy requirements first but don't install llama-cpp-python yet
COPY requirements.txt .
RUN grep -v "llama-cpp-python" requirements.txt > requirements_without_llama.txt && \
    pip install --no-cache-dir -r requirements_without_llama.txt

# Install llama-cpp-python with GPU support
ENV CMAKE_ARGS="-DLLAMA_CUBLAS=on"
ENV FORCE_CMAKE=1
RUN pip install --no-cache-dir llama-cpp-python==0.2.63

# Copy the rest of the application
COPY . .

# Create required directories
RUN mkdir -p ./models ./uploads

# Create entrypoint script
RUN echo '#!/bin/bash\n\
MODEL_PATH=${MODEL_PATH:-./models/llama-2-7b.Q4_K_M.gguf}\n\
if [ ! -f "$MODEL_PATH" ]; then\n\
  echo "🔄 Model not found. Installing dependencies and downloading..."\n\
  pip install --no-cache-dir huggingface_hub\n\
  python download_model.py\n\
fi\n\
# Start the application\n\
exec uvicorn api:app --host 0.0.0.0 --port 8000\n\
' > /app/entrypoint.sh

# Set proper permissions
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/bin/bash", "/app/entrypoint.sh"]
