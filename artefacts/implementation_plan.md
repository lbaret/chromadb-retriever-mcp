# Tabular Document Retriever - Implementation Plan

We will build the Tabular Document Retriever according to the project specifications.

## Proposed Changes

We will create a structured Python project leveraging `uv` for dependency management.

---

### Project Structure and Dependencies
The project will use `pyproject.toml` generated with the required dependencies: `pandas`, `chromadb`, `mcp`, `mcp[cli]`, `openpyxl`, `sentence-transformers`, `fastapi`, and `uvicorn`.

#### [NEW] [pyproject.toml](file:///home/lbaret/chromadb-mcp/pyproject.toml)
Setup file for `uv` including all required ML and MCP dependencies.

#### [NEW] [.python-version](file:///home/lbaret/chromadb-mcp/.python-version)
Specifying `3.12.12`.

---
### Server & Core Logic

We will split the logic across focused modules under the `src` directory.

#### [NEW] [src/ingestor.py](file:///home/lbaret/chromadb-mcp/src/ingestor.py)
* **Goal**: Provides logic to load CSV/XLSX files using `pandas`, convert rows into markdown strings (`Column: Value` format), and extract metadata dictionary.
* **Details**: Will have a CLI function to read a file path and ingest it into ChromaDB.

#### [NEW] [src/database.py](file:///home/lbaret/chromadb-mcp/src/database.py)
* **Goal**: Initializes the ChromaDB client.
* **Details**: Connects to the ChromaDB server (via HTTP if running in Docker, or local mode). Includes functions to get or create collections, and upsert documents + metadata + embeddings. It will use the `SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")`.

#### [NEW] [src/retriever.py](file:///home/lbaret/chromadb-mcp/src/retriever.py)
* **Goal**: Implements search logic.
* **Details**: Takes a query string, embeds it or delegates to ChromaDB, and returns top-K documents and their metadata.

#### [NEW] [src/server.py](file:///home/lbaret/chromadb-mcp/src/server.py)
* **Goal**: The main MCP server application.
* **Details**: Since we need to "Expose ONLY the MCP server port", we will implement an SSE-based Server using FastAPI and the `mcp.server.fastapi` (or `mcp`'s built-in FastMCP). It will define the tools: `retrieve_batch`, `retrieve_single`, and `retrieve_by_query`.

---
### Deployment & Containerization

#### [NEW] [Dockerfile](file:///home/lbaret/chromadb-mcp/Dockerfile)
* **Goal**: A multi-stage Docker build copying our source code, installing dependencies with `uv`, and setting up the entrypoint for the MCP Server using uvicorn/fastapi on a specific port (e.g., 8000).

#### [NEW] [docker-compose.yml](file:///home/lbaret/chromadb-mcp/docker-compose.yml)
* **Goal**: Defines the multi-container environment.
* **Details**: 
  - `mcp-app`: Builds from `Dockerfile`, ports `8000:8000`.
  - `chroma-db`: Uses `chromadb/chroma:latest` image. Internal access only.

#### [NEW] [README.md](file:///home/lbaret/chromadb-mcp/README.md)
* **Goal**: Documentation on how to run the components (ingestion CLI and turning on Docker Compose).

## Verification Plan
1. We will verify the `uv` setup works correctly.
2. We will test `ingestor.py` by creating a dummy `.csv` file and observing ChromaDB ingestion.
3. We will start the `docker-compose` stack and curl the MCP server or test the `/sse` endpoint manually or using the `mcp` client CLI.

## User Review Required
> [!IMPORTANT]  
> The prompt implies exposing the server via a port ("Expose ONLY the MCP server port to the host"). I will implement the MCP server using SSE (Server-Sent Events) over HTTP with FastAPI/Uvicorn, since standard stdio MCP servers don't bind to a port. Is this correct?
