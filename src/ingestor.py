import hashlib
import logging
import os

import click
import pandas as pd

from src.database import get_chroma_client, get_or_create_collection, upsert_records

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.command(help="Ingest tabular data to ChromaDB")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--embed-columns", "-c", multiple=True, help="Specific columns to include in the embedded document content.")
def process_file(file_path: str, embed_columns: tuple | list = ()) -> None:
    """
    Reads a CSV or Excel file, processes each row into a markdown string,
    and upserts the data into ChromaDB.
    
    Args:
        file_path (str): The path to the CSV or Excel file to process.
        embed_columns (tuple | list): List of columns to include in the embedded document content. If empty, all columns are used.
    """
    logger.info(f"Reading file: {file_path}")
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError("Unsupported file format. Use .csv or .xlsx")
    
    ids = []
    documents = []
    metadatas = []
    
    seen_ids = set()
    
    for _, row in df.iterrows():
        # Convert row to dictionary, dropping NaNs
        row_dict = {str(k): str(v) for k, v in row.items() if pd.notna(v)}
        
        # Skip completely empty rows
        if not row_dict:
            continue
            
        # Create markdown string
        if embed_columns:
            md_lines = [f"{k}: {v}" for k, v in row_dict.items() if k in embed_columns]
            if not md_lines:
                continue # Skip if none of the specified columns are present
        else:
            md_lines = [f"{k}: {v}" for k, v in row_dict.items()]
        md_string = "\n".join(md_lines)
        
        # Generate stable ID
        row_hash = hashlib.sha256(md_string.encode('utf-8')).hexdigest()
        
        if row_hash in seen_ids:
            continue
        seen_ids.add(row_hash)
        
        ids.append(row_hash)
        documents.append(md_string)
        metadatas.append(row_dict)
    
    logger.info(f"Processed {len(documents)} rows. Upserting to ChromaDB...")
    
    client = get_chroma_client(
        auth_provider=os.getenv("CHROMA_CLIENT_AUTH_PROVIDER"),
        auth_credentials=os.getenv("CHROMA_CLIENT_AUTH_CREDENTIALS")
    )
    collection = get_or_create_collection(client)
    
    # Batch upsert in chunks 
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        upsert_records(
            collection, 
            ids[i:i+batch_size], 
            documents[i:i+batch_size], 
            metadatas[i:i+batch_size]
        )
        logger.info(f"Upserted batch {i//batch_size + 1}/{(len(ids)-1)//batch_size + 1}")
        
    logger.info("Ingestion complete!")

if __name__ == "__main__":
    process_file()
