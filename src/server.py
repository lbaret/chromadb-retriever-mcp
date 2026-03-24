import logging
from typing import Any, Dict, List

from north_mcp_python_sdk import NorthMCPServer

from src.retriever import retrieve

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an MCP server instance configured for North exposure
mcp = NorthMCPServer("tabular-document-retriever", host="0.0.0.0", port=8000)

@mcp.tool()
def retrieve_batch(rows: List[str], top_k: int = 5, where: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """
    Performs a batch semantic similarity search against the ChromaDB vector database.
    
    This tool is designed to accept an array of strings (e.g., Markdown-formatted table rows, 
    or plain text queries) and individually retrieves the most relevant matched documents for each item. 
    It is extremely useful when you have multiple records to cross-reference against the database at once.

    Parameters:
        rows (List[str]): A list of string queries or markdown rows to search for.
        top_k (int, optional): The maximum number of relevant matches to return for EACH row. Defaults to 5.
        where (Dict[str, Any], optional): A ChromaDB-compatible metadata filter dictionary. 
                                          Use this to narrow down the search context. Defaults to None.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dict contains the original 'query' and 
                              a 'matches' list containing the retrieved records and their distances.

    Example Usage:
        retrieve_batch(
            rows=["Population of Quebec", "Population of Ontario"], 
            top_k=2,
            where={"Year": "2021"}
        )
    """
    all_matches = []
    for row in rows:
        matches = retrieve(row, top_k=top_k, where=where)
        all_matches.append({
            "query": row,
            "matches": matches
        })
    return all_matches

@mcp.tool()
def retrieve_single(row: str, top_k: int = 5, where: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Performs a semantic similarity search against the ChromaDB database for a single query.
    
    This tool is optimized for finding contextually related documents based on a single input string. 
    It is ideal for mapping a single record or answering a localized semantic query by retrieving 
    the nearest embeddings stored in the vector database.

    Parameters:
        row (str): The string query or formatted markdown row to match against the database.
        top_k (int, optional): The maximum number of relevant matches to return. Defaults to 5.
        where (Dict[str, Any], optional): A ChromaDB-compatible metadata filter dictionary. 
                                          Use this to narrow down the search context. Defaults to None.
    
    Returns:
        Dict[str, Any]: A dictionary containing the original 'query' and its resulting 'matches' list.

    Example Usage:
        retrieve_single(
            row="What is the total revenue for branch A?", 
            top_k=3,
            where={"Department": "Sales"}
        )
    """
    return {
        "query": row,
        "matches": retrieve(row, top_k=top_k, where=where)
    }

@mcp.tool()
def retrieve_by_query(query: str, top_k: int = 5, where: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Executes a flexible, free-form semantic search query against the ChromaDB database.
    
    Use this tool when you need to ask a broad question, supply instructions, or pass a general 
    string that isn't formatted strictly as a 'row'. It will retrieve the most semantically 
    relevant text chunks or tabular records stored within the system.

    Parameters:
        query (str): The raw text query to search for.
        top_k (int, optional): The maximum number of results to fetch. Defaults to 5.
        where (Dict[str, Any], optional): A ChromaDB-compatible metadata filter dictionary. 
                                          Use this to strict-filter the result contexts. Defaults to None.
    
    Returns:
        Dict[str, Any]: A dictionary containing the original 'query' and its resulting 'matches' list.

    Example Usage:
        retrieve_by_query(
            query="Show me all the municipal data for regions exceeding 50,000 residents", 
            top_k=10,
            where={"Region": "Quebec", "Data_Type": "Census"}
        )
    """
    return {
        "query": query,
        "matches": retrieve(query, top_k=top_k, where=where)
    }

if __name__ == "__main__":
    # Start the server using streamable-http transport for North compatibility
    logger.info(
        "Starting Tabular Document Retriever MCP server on port 8000 (streamable-http)..."
    )
    mcp.run(transport="streamable-http")
