#!/bin/bash
set -e

echo "🚀 Starting frontend development server..."

# Change to frontend directory
cd frontend

# Set the API URL environment variable pointing to the local backend
export VITE_API_URL=http://localhost:8000

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js and npm first."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting frontend server..."
npm run dev -- --host 0.0.0.0

echo "Frontend server stopped."
