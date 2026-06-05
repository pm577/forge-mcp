"""
Deploy Forge with Docker.
"""
import subprocess

DOCKERFILE = """
FROM python:3.11-slim
WORKDIR /app
RUN pip install forge-mcp
EXPOSE 4243
CMD ["forge-server", "--port", "4243"]
"""

DOCKER_COMPOSE = """
version: '3.8'
services:
  forge:
    build: .
    ports:
      - "4243:4243"
    volumes:
      - forge_data:/root/.forge
    restart: unless-stopped
    command: forge-server --port 4243

volumes:
  forge_data:
"""

# Write files
with open("Dockerfile", "w") as f:
    f.write(DOCKERFILE.strip() + "\n")
with open("docker-compose.yml", "w") as f:
    f.write(DOCKER_COMPOSE.strip() + "\n")
print("Docker deployment files created")
print("Run: docker compose up -d")
