# Role
You are an expert Full-Stack Software Architect and Python Developer. Your goal is to build a high-performance "Tabular Document Retriever" using the Model Context Protocol (MCP).

# Objective
Create a Python-based MCP server that ingests Excel/CSV files, processes them into Markdown key-value pairs, stores them in ChromaDB, and provides a sophisticated retrieval interface.

# Architecture & Technical Requirements

## 1. Data Ingestion & Transformation (`ingestor.py`)
- Use `pandas` to read `.xlsx` and `.csv` files.
- **Processing Logic**: Iterate through each row and convert it into a Markdown key-value string.
  - *Example*: `Column1: Value1 | Column2: Value2` becomes:
    ```markdown
    Column1: Value1
    Column2: Value2
    ```
- Ensure all original row data is preserved in a dictionary to be used as **metadata** in the vector database.

## 2. Vector Database Integration (`database.py`)
- Configure a client for **ChromaDB**.
- Implement logic to create a collection and upsert data.
- **Documents**: The Markdown key-value string.
- **Metadatas**: The full row dictionary.
- **Embeddings**: Use a standard local embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`).

## 3. Retrieval Engine (`retriever.py`)
- Create a retrieval function that:
  - Takes a Markdown key-value string as input.
  - Performs a similarity search (Top-K) against ChromaDB.
  - Returns the relevant documents along with their associated metadata.

## 4. MCP Server Implementation (`server.py`)
- Use the `mcp` Python SDK to expose the following **tools**:
  - `retrieve_batch`: Accepts a list of table rows (as Markdown) and returns matches.
  - `retrieve_single`: Accepts one example row and returns matches.
  - `retrieve_by_query`: Accepts a pre-constructed query string for flexible searching.
- Implementation must follow the MCP standard (stdio or SSE support).

## 5. Deployment & Containerization
- **Dockerfile**: Create a multi-stage build for the MCP server application.
- **Docker Compose**: Define a multi-container environment:
  - `mcp-app`: The Python server.
  - `chroma-db`: The official ChromaDB image.
  - **Networking**: Link them in a private network. Expose ONLY the MCP server port to the host.

# Deliverables
1. Complete Python source code for all modules.
2. `pyproject.toml` with `uv` tool, necessary dependencies (pandas, chromadb, mcp, openpyxl, sentence-transformers).
3. `Dockerfile` and `docker-compose.yml`.
4. A `README.md` explaining how to run the ingestion and start the server.

# Quality Standards
- Write clean, modular, and well-documented Python code.
- Implement robust error handling for file I/O and DB connections.
- Ensure the retrieval logic is optimized for tabular data context.