#!/bin/bash
set -e

echo "🚀 Pushing all current changes to new branch V2..."

# Create necessary directories and placeholder files
echo "📁 Creating directory placeholders..."
mkdir -p backend/models backend/uploads/audio
touch backend/models/.gitkeep
touch backend/uploads/.gitkeep
touch backend/uploads/audio/.gitkeep

# Create the new branch
echo "🔀 Creating new branch V2..."
git checkout -b V2

# Add all changes
echo "➕ Adding all changes to staging..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Version 2: Multi-agent system with audio podcast generation"

# Push the new branch to remote
echo "☁️ Pushing branch V2 to remote repository..."
git push -u origin V2

echo "✅ Successfully pushed all changes to branch V2!"
echo "📊 Access the branch on GitHub via: https://github.com/yourusername/MultAgent-Research-Paper-Summarizer/tree/V2"
