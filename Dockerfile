# Cloud Run image: needs Python (for ADK) AND Node (so `npx mongodb-mcp-server` works).
FROM python:3.12-slim

# Install Node 22 — needed by `npx mongodb-mcp-server` which the agent spawns.
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Pre-cache the MCP server so we don't pay npx-fetch latency on first request.
RUN npm install -g mongodb-mcp-server@latest

WORKDIR /app
COPY pyproject.toml ./
COPY agent ./agent
RUN pip install --no-cache-dir .

ENV PORT=8080
EXPOSE 8080

# Use ADK's deploy-time wrapper for the FastAPI app + chat UI.
CMD ["adk", "web", "--host=0.0.0.0", "--port=8080", "."]
