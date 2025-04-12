FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git curl build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create required directories
RUN mkdir -p ./models ./uploads

# Download model script
COPY download_model.py .

# Create an entrypoint script to check for the model and download if needed
RUN echo '#!/bin/bash \n\
MODEL_PATH=${MODEL_PATH:-./models/llama-2-7b.Q4_K_M.gguf} \n\
if [ ! -f "$MODEL_PATH" ]; then \n\
  echo "🔄 Model not found. Installing dependencies and downloading..." \n\
  pip install --no-cache-dir huggingface_hub \n\
  python download_model.py \n\
fi \n\
# Start the application \n\
exec uvicorn api:app --host 0.0.0.0 --port 8000 \n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
