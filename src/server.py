import logging
from typing import Any, Dict, List

from north_mcp_python_sdk import NorthMCPServer

from src.retriever import retrieve

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an MCP server instance configured for North exposure
mcp = NorthMCPServer("tabular-document-retriever", host="0.0.0.0", port=8000)

@mcp.tool()
def retrieve_batch(rows: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Accepts a list of table rows (as Markdown or plain text query) and returns 
    relevant matches from the database for each.
    """
    all_matches = []
    for row in rows:
        matches = retrieve(row, top_k=top_k)
        all_matches.append({
            "query": row,
            "matches": matches
        })
    return all_matches

@mcp.tool()
def retrieve_single(row: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Accepts one example row (as Markdown) and returns relevant matches based on semantic similarity.
    """
    return {
        "query": row,
        "matches": retrieve(row, top_k=top_k)
    }

@mcp.tool()
def retrieve_by_query(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Accepts a pre-constructed free-form query string for flexible searching and returns matches.
    """
    return {
        "query": query,
        "matches": retrieve(query, top_k=top_k)
    }

if __name__ == "__main__":
    # Start the server using streamable-http transport for North compatibility
    logger.info(
        "Starting Tabular Document Retriever MCP server on port 8000 (streamable-http)..."
    )
    mcp.run(transport="streamable-http")
