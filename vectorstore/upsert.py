import logging
from qdrant_client import QdrantClient
from core.load_settings import load_settings
from vectorstore.qdrant import get_qdrant_client, ensure_collection
from vectorstore.index import build_qdrant_points

settings = load_settings()
logger = logging.getLogger("vector_database")

QRANT_CONFIG = settings["vector_database"]
COLLECTION_NAME = QRANT_CONFIG["collection_name"]

def upsert_chunks(chunks: list[dict]):
    if not chunks:
        logger.warning("No chunks provided to build Qdrant points.")
        return []

    client:QdrantClient = get_qdrant_client() # lấy client từ qdrant.py
    ensure_collection(client)    # đảm bảo collection tồn tại

    points = build_qdrant_points(chunks) # tạo các point từ chunks

    if not points:
        logger.warning("No points were built from the provided chunks.")
        return []

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    ) # upsert vào collection

    logger.info(f"Upserted {len(points)} points into collection '{COLLECTION_NAME}'.")
