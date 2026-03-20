import os
import logging
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logger = logging.getLogger(__name__)

def get_chroma_client() -> "chromadb.api.ClientAPI":
    """
    Returns a ChromaDB client. 
    Uses HTTP client if CHROMA_HOST and CHROMA_PORT are provided.
    Otherwise, uses a local persistent client.
    """
    host = os.getenv("CHROMA_HOST", "localhost")
    port = os.getenv("CHROMA_PORT", "")
    
    if port:
        return chromadb.HttpClient(host=host, port=port)
    else:
        # Fallback to local persistent client (mainly for local testing of ingestor without Docker)
        return chromadb.PersistentClient(path="./chroma_data")

def get_or_create_collection(client: "chromadb.api.ClientAPI", collection_name: str = "tabular_data") -> "chromadb.api.models.Collection.Collection":
    """
    Creates or retrieves the ChromaDB collection with the correct embedding function.
    """
    # Using the standard local embedding model as requested
    emb_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=emb_fn
    )

def upsert_records(collection: "chromadb.api.models.Collection.Collection", ids: list[str], documents: list[str], metadatas: list[dict[str, str]]) -> None:
    """
    Upserts records into ChromaDB collection.
    """
    if not ids:
        return
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
