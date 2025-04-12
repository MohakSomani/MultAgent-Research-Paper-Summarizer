#!/bin/bash
# filepath: /home/mohak/Desktop/MultAgent-Research-Paper-Summarizer/run.sh

# Stop running containers
docker compose down

# Remove all stopped containers, dangling images, and unused networks
echo "======================Cleaning up inactive containers and freeing space...======================"
docker container prune -f
docker image prune -f
docker network prune -f

# Alternative: Use system prune for a more thorough cleanup (uncomment if needed)
# docker system prune -f

# Build containers
echo "======================Building containers...======================"
docker compose build

# Start services
echo "======================Starting services...======================"
docker compose up -d

# Follow logs
echo "======================Displaying logs...======================"
docker compose logs -f