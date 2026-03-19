import chromadb

def dump_records():
    # Connect to the ChromaDB container using the exposed port 8001
    client = chromadb.HttpClient(host="localhost", port=8001)
    
    # Get the collection (default from your database.py is 'tabular_data')
    collection_name = "tabular_data"
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Failed to get collection '{collection_name}': {e}")
        return

    # Fetch all records by not passing any specific ids
    # You can specify the fields you want to include in the output
    results = collection.get(
        include=["documents", "metadatas", "embeddings"]
    )
    
    total_records = len(results.get("ids", []))
    print(f"Total records found in '{collection_name}': {total_records}")
    
    # Print the records
    for i in range(total_records):
        record_id = results["ids"][i]
        document = results["documents"][i] if results.get("documents") else None
        metadata = results["metadatas"][i] if results.get("metadatas") else None
        
        print(f"\n--- Record {i+1} ---")
        print(f"ID: {record_id}")
        print(f"Metadata: {metadata}")
        print(f"Document:\n{document}")

if __name__ == "__main__":
    dump_records()
