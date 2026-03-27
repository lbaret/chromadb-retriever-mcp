import hashlib
import io
import logging
import os
import typing

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from src.database import get_chroma_client, get_or_create_collection, upsert_records

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="ChromaDB Ingestion API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}


def _ingest_dataframe(
    df: pd.DataFrame, embed_columns: tuple | list = ()
) -> dict[str, typing.Any]:
    """
    Process a DataFrame into ChromaDB.
    Returns a summary dict with rows_processed and duplicates_skipped.
    """
    ids = []
    documents = []
    metadatas = []
    seen_ids: set[str] = set()

    for _, row in df.iterrows():
        row_dict = {str(k): str(v) for k, v in row.items() if pd.notna(v)}
        if not row_dict:
            continue

        if embed_columns:
            md_lines = [f"{k}: {v}" for k, v in row_dict.items() if k in embed_columns]
            if not md_lines:
                continue
        else:
            md_lines = [f"{k}: {v}" for k, v in row_dict.items()]
        md_string = "\n".join(md_lines)

        row_hash = hashlib.sha256(md_string.encode("utf-8")).hexdigest()
        if row_hash in seen_ids:
            continue
        seen_ids.add(row_hash)

        ids.append(row_hash)
        documents.append(md_string)
        metadatas.append(row_dict)

    total_rows = len(df)
    duplicates_skipped = total_rows - len(ids)

    logger.info(f"Processed {len(ids)} unique rows (skipped {duplicates_skipped} duplicates). Upserting...")

    client = get_chroma_client(
        auth_provider=os.getenv("CHROMA_CLIENT_AUTH_PROVIDER"),
        auth_credentials=os.getenv("CHROMA_CLIENT_AUTH_CREDENTIALS")
    )
    collection = get_or_create_collection(client)

    batch_size = 500
    for i in range(0, len(ids), batch_size):
        upsert_records(
            collection,
            ids[i : i + batch_size],
            documents[i : i + batch_size],
            metadatas[i : i + batch_size],
        )
        logger.info(f"Upserted batch {i // batch_size + 1}/{(len(ids) - 1) // batch_size + 1}")

    logger.info("Ingestion complete!")
    return {
        "status": "ok",
        "rows_processed": len(ids),
        "duplicates_skipped": duplicates_skipped,
    }


@app.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...), embed_columns: list[str] = Query(default=[])
) -> dict[str, typing.Any]:
    """
    Upload a CSV or Excel file to ingest into ChromaDB.
    Returns a JSON summary with the number of rows processed.
    """
    filename = file.filename or ""
    contents = await file.read()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a .csv or .xlsx file.",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    try:
        result = _ingest_dataframe(df, embed_columns)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return result
