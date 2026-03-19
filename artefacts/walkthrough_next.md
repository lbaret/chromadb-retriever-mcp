# Walkthrough: FastAPI Ingestion REST API

## Changes Made

### [NEW] [api.py](file:///home/lbaret/chromadb-mcp/src/api.py)
FastAPI app with two endpoints:
- **`GET /health`** — returns `{"status": "ok"}`
- **`POST /ingest/file`** — accepts a CSV/XLSX file upload, ingests it into ChromaDB, and returns a summary

Reuses [database.py](file:///home/lbaret/chromadb-mcp/src/database.py) for all ChromaDB operations. Ingestion logic mirrors [ingestor.py](file:///home/lbaret/chromadb-mcp/src/ingestor.py) but is decoupled from the Click CLI.

### [MODIFY] [docker-compose.yml](file:///home/lbaret/chromadb-mcp/docker-compose.yml)
- **ChromaDB** port `8001:8000` exposed to the host
- **New `ingestion-api` service** on port `8080`, overriding the default `CMD` to run uvicorn with `src.api:app`

```diff:docker-compose.yml
version: "3.8"

services:
  mcp-app:
    build: .
    ports:
      - "8000:8000" # Expose ONLY the MCP server port to the host
    environment:
      - CHROMA_HOST=chroma-db
      - CHROMA_PORT=8000
    depends_on:
      - chroma-db
    networks:
      - mcp-network

  chroma-db:
    image: chromadb/chroma:latest
    volumes:
      - chroma-data:/chroma/chroma
    # We deliberately do not publish ports for chroma-db to ensure it remains private
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge

volumes:
  chroma-data:
===
version: "3.8"

services:
  mcp-app:
    build: .
    ports:
      - "8000:8000" # Expose ONLY the MCP server port to the host
    environment:
      - CHROMA_HOST=chroma-db
      - CHROMA_PORT=8000
    depends_on:
      - chroma-db
    networks:
      - mcp-network

  ingestion-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - CHROMA_HOST=chroma-db
      - CHROMA_PORT=8000
    depends_on:
      - chroma-db
    command: ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8080"]
    networks:
      - mcp-network

  chroma-db:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000" # Expose ChromaDB to the host
    volumes:
      - chroma-data:/chroma/chroma
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge

volumes:
  chroma-data:
```

### [MODIFY] [Dockerfile](file:///home/lbaret/chromadb-mcp/Dockerfile)
Added [README.md](file:///home/lbaret/chromadb-mcp/README.md) to the `COPY` in the builder stage so `hatchling` can resolve it during `uv sync`.

```diff:Dockerfile
# Stage 1: Build environment
FROM python:3.12.12-slim as builder

# Install uv compiler dependencies
RUN pip install uv

WORKDIR /app
# Copy the dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen

# Stage 2: Final runtime
FROM python:3.12.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY ./src /app/src

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Configuration for Database connection
ENV CHROMA_HOST="chroma-db"
ENV CHROMA_PORT="8000"

# Expose the port for the SSE server
EXPOSE 8000

# Start the MCP server using python
CMD ["python", "src/server.py"]
===
# Stage 1: Build environment
FROM python:3.12.12-slim as builder

# Install uv compiler dependencies
RUN pip install uv

WORKDIR /app
# Copy the dependency files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies into a virtual environment
RUN uv sync --frozen

# Stage 2: Final runtime
FROM python:3.12.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY ./src /app/src

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Configuration for Database connection
ENV CHROMA_HOST="chroma-db"
ENV CHROMA_PORT="8000"

# Expose the port for the SSE server
EXPOSE 8000

# Start the MCP server using python
CMD ["python", "src/server.py"]
```

## Verification Results

| Test | Result |
|------|--------|
| `GET /health` | ✅ `{"status":"ok"}` |
| ChromaDB heartbeat (port 8001) | ✅ Reachable |
| `POST /ingest/file` with [Pop-MUN-25000+.xlsx](file:///home/lbaret/chromadb-mcp/data/Pop-MUN-25000+.xlsx) | ✅ `{"status":"ok","rows_processed":58,"duplicates_skipped":5}` |
