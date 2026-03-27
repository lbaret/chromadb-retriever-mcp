import os
from src.retriever import retrieve

# Set the same auth variables as docker-compose 
# since we are running this script directly against the dockerized ChromaDB exposed on port 8001
os.environ["CHROMA_HOST"] = "localhost"
os.environ["CHROMA_PORT"] = "8001"
os.environ["CHROMA_CLIENT_AUTH_PROVIDER"] = "chromadb.auth.token_authn.TokenAuthClientProvider"
os.environ["CHROMA_CLIENT_AUTH_CREDENTIALS"] = "test-auth-token"

print("Testing direct retrieval...")
results = retrieve("Population count")
print(f"Retrieved {len(results)} items.")
if len(results) > 0:
    for i, res in enumerate(results[:2]):
        print(f"Match {i+1} Distance: {res['distance']}")
        print(f"Match {i+1} Metadata: {res['metadata']}")
    print("Direct retrieval test PASSED.")
else:
    print("Direct retrieval test FAILED: No items retrieved.")
