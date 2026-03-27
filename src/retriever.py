import logging
import typing
import os

from src.database import get_chroma_client, get_or_create_collection

logger = logging.getLogger(__name__)

def retrieve(query_string: str, top_k: int = 50, where: dict[str, typing.Any] | None = None) -> list[dict[str, typing.Any]]:
    """
    Takes a query string and performs a similarity search against ChromaDB.
    Returns the relevant documents along with their associated metadata.
    """
    client = get_chroma_client(
        auth_provider=os.getenv("CHROMA_CLIENT_AUTH_PROVIDER"),
        auth_credentials=os.getenv("CHROMA_CLIENT_AUTH_CREDENTIALS")
    )
    collection = get_or_create_collection(client)
    
    # ChromaDB handles the embedding using the specified SentenceTransformer function
    query_kwargs = {
        "query_texts": [query_string],
        "n_results": top_k
    }
    if where:
        query_kwargs["where"] = where
        
    results = collection.query(**query_kwargs)
    
    # Format the results nicely
    matches = []
    if results['documents'] and len(results['documents']) > 0:
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results else []
        
        for i in range(len(docs)):
            matches.append({
                "document": docs[i] if docs else None,
                "metadata": metas[i] if metas else None,
                "distance": distances[i] if i < len(distances) else None
            })
            
    return matches
