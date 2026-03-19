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
