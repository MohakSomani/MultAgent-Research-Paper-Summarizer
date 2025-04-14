#!/bin/bash
set -e

# Main setup script for MultAgent Research Paper Summarizer

echo "🚀 Setting up MultAgent Research Paper Summarizer..."

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/models backend/uploads/audio

# 1. Create Python virtual environment in backend folder if not already present
if [ ! -d "backend/.venv" ]; then
    echo "🐍 Creating Python virtual environment in backend folder..."
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    cd ..
else
    echo "✅ Python virtual environment already exists in backend folder."
fi

# # 2. Install system dependencies
# echo "📦 Installing system dependencies..."

# # Detect OS
# if [[ "$OSTYPE" == "linux-gnu"* ]]; then
#     # Check for apt (Debian/Ubuntu)
#     if command -v apt-get &> /dev/null; then
#         echo "📦 Installing dependencies using apt..."
#         sudo apt-get update
#         sudo apt-get install -y build-essential cmake espeak python3-dev
        
#         # Check for NVIDIA GPU
#         if command -v nvidia-smi &> /dev/null; then
#             echo "🖥️ NVIDIA GPU detected, installing CUDA dependencies..."
#             # Add universe repository which contains libtinfo5
#             sudo apt-add-repository universe -y
#             sudo apt-get update
#             sudo apt-get install -y libtinfo5 libncurses5
#         fi
#     # Check for yum/dnf (RHEL/CentOS/Fedora)
#     elif command -v dnf &> /dev/null || command -v yum &> /dev/null; then
#         echo "📦 Installing dependencies using yum/dnf..."
#         sudo dnf install -y gcc-c++ cmake espeak python3-devel || sudo yum install -y gcc-c++ cmake espeak python3-devel
#     else
#         echo "⚠️ Unknown Linux distribution, please install these packages manually:"
#         echo "   - build-essential/gcc-c++"
#         echo "   - cmake"
#         echo "   - espeak"
#         echo "   - python3-dev/python3-devel"
#     fi
# elif [[ "$OSTYPE" == "darwin"* ]]; then
#     # macOS
#     if command -v brew &> /dev/null; then
#         echo "📦 Installing dependencies using Homebrew..."
#         brew install cmake espeak
#     else
#         echo "⚠️ Homebrew not found. Please install it first:"
#         echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
#         echo "   Then run this script again."
#         exit 1
#     fi
# else
#     echo "⚠️ Unsupported OS: $OSTYPE"
#     echo "Please install the following dependencies manually:"
#     echo "   - C++ compiler (gcc/g++/clang++)"
#     echo "   - cmake"
#     echo "   - espeak"
#     echo "   - Python development headers"
# fi

# 3. Upgrade pip and install Python packages
echo "📦 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt

# 3.1 Setup frontend dependencies if needed
if [ -d "frontend" ]; then
    echo "📦 Setting up frontend dependencies..."
    if command -v npm &> /dev/null; then
        (cd frontend && npm install)
    else
        echo "⚠️ npm not found. Frontend dependencies not installed."
        echo "   Install Node.js and npm, then run: cd frontend && npm install"
    fi
fi

# 4. Check for Llama model and download if needed
MODEL_PATH="backend/models/llama-2-7b.Q4_K_M.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    echo "🔄 Model not found, downloading from Huggingface..."
    pip install --no-cache-dir huggingface_hub
    python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='TheBloke/Llama-2-7B-GGUF', filename='llama-2-7b.Q4_K_M.gguf', local_dir='./backend/models')"
else
    echo "✅ Model already exists at $MODEL_PATH"
fi

echo "✅ Setup complete! You can now run the backend with: ./LOCAL_run_backend.sh"
