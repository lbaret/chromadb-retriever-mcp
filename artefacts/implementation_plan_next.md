# FastAPI Ingestion REST API for ChromaDB

Convert the existing CLI-based ingestion script ([src/ingestor.py](file:///home/lbaret/chromadb-mcp/src/ingestor.py)) into a REST API powered by FastAPI, and expose the ChromaDB container so the API service can reach it.

## User Review Required

> [!IMPORTANT]
> The current [docker-compose.yml](file:///home/lbaret/chromadb-mcp/docker-compose.yml) deliberately keeps the ChromaDB port **private** (no `ports:` mapping). This plan opens port `8001` on the host to reach the ChromaDB container and adds a new `ingestion-api` service on port `8080`. Please confirm these port assignments work for you.

> [!NOTE]
> The existing MCP server ([src/server.py](file:///home/lbaret/chromadb-mcp/src/server.py)) and CLI ingestor ([src/ingestor.py](file:///home/lbaret/chromadb-mcp/src/ingestor.py)) remain **untouched**. The new FastAPI app is a separate module (`src/api.py`) that reuses [database.py](file:///home/lbaret/chromadb-mcp/src/database.py) logic.

## Proposed Changes

### Docker / Infrastructure

#### [MODIFY] [docker-compose.yml](file:///home/lbaret/chromadb-mcp/docker-compose.yml)

1. **Expose ChromaDB port** — add `ports: - "8001:8000"` to the `chroma-db` service so it is reachable from the host.
2. **Add `ingestion-api` service** — a new container built from the same [Dockerfile](file:///home/lbaret/chromadb-mcp/Dockerfile), running the FastAPI app on port `8080`, connected to the same `mcp-network`, with `CHROMA_HOST=chroma-db` and `CHROMA_PORT=8000`.

#### [MODIFY] [Dockerfile](file:///home/lbaret/chromadb-mcp/Dockerfile)

- No structural changes needed. The same image already has FastAPI + uvicorn. The `CMD` will be overridden via `command:` in [docker-compose.yml](file:///home/lbaret/chromadb-mcp/docker-compose.yml) for the `ingestion-api` service.

---

### Application Code

#### [NEW] [api.py](file:///home/lbaret/chromadb-mcp/src/api.py)

A new FastAPI application with the following endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/ingest/file` | Upload a CSV or Excel file; the API ingests it into ChromaDB and returns a summary (rows processed, batches upserted). |
| `GET` | `/health` | Simple health check returning `{"status": "ok"}`. |

Key design decisions:
- Accepts file uploads via `UploadFile` (multipart/form-data).
- Reuses [database.py](file:///home/lbaret/chromadb-mcp/src/database.py) functions ([get_chroma_client](file:///home/lbaret/chromadb-mcp/src/database.py#8-22), [get_or_create_collection](file:///home/lbaret/chromadb-mcp/src/database.py#23-33), [upsert_records](file:///home/lbaret/chromadb-mcp/src/database.py#34-45)).
- Extracts the ingestion logic from [ingestor.py](file:///home/lbaret/chromadb-mcp/src/ingestor.py) into a reusable helper function (within `api.py` itself) that takes a `pandas.DataFrame` and upserts it, so we avoid coupling with the click CLI.
- Returns a JSON response: `{"status": "ok", "rows_processed": N, "duplicates_skipped": M}`.

---

### Dependencies

No new dependencies — `fastapi`, `uvicorn`, `pandas`, `openpyxl` are all already in [pyproject.toml](file:///home/lbaret/chromadb-mcp/pyproject.toml).

## Verification Plan

### Automated Tests

1. **Build & start the stack**:
   ```bash
   cd /home/lbaret/chromadb-mcp
   docker compose up --build -d
   ```

2. **Health check**:
   ```bash
   curl http://localhost:8080/health
   # Expected: {"status":"ok"}
   ```

3. **Ingest the sample file**:
   ```bash
   curl -X POST http://localhost:8080/ingest/file \
     -F "file=@data/Pop-MUN-25000+.xlsx"
   # Expected: JSON with rows_processed > 0
   ```

4. **Verify ChromaDB is reachable** on the exposed port:
   ```bash
   curl http://localhost:8001/api/v1/heartbeat
   # Expected: a JSON heartbeat response
   ```

5. **Tear down**:
   ```bash
   docker compose down
   ```
