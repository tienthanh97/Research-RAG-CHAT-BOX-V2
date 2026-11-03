from embedding.sparse_embedder import SparseEmbedder # sparse embedding
from embedding.embed_texts import embed_texts
import logging
import uuid

logger = logging.getLogger("vector_database")

_sparse_embedder: SparseEmbedder | None = None

def init_sparse_embedder(embedder: SparseEmbedder):
    global _sparse_embedder
    _sparse_embedder = embedder # initialize sparse embedder for hybrid index
    logger.info("Sparse embedder initialized for hybrid index.")

def build_hybrid_qdrant_points(chunks: list[dict]) -> list[dict]:
    if not chunks:
        logger.warning("No chunks provided to build Qdrant points.")
        return []

    if _sparse_embedder is None:
        raise RuntimeError("Sparse embedder is not initialized. Call init_sparse_embedder first.")

    texts = [chunk["text"] for chunk in chunks]
    if not texts:
        logger.warning("No text found in the provided chunks.")
        return []

    dense_embeddings = embed_texts(texts)
    sparse_embeddings = _sparse_embedder.encode_batch(texts)
    points = []

    for chunk, dense_vector, sparse_vector in zip(chunks, dense_embeddings, sparse_embeddings):
        points.append({
            "id": str(uuid.uuid4()), # tao duy nhat cho tung point
            "vector": dense_vector, # embedding vector
            "sparse_vector": {
                "indices": sparse_vector["indices"].tolist(),
                "values": sparse_vector["values"].tolist(),
            },
            "payload": {
                "text": chunk["text"],
                **chunk.get("metadata", {}) # them metadata neu co
            }
        })

    logger.info(f"Built {len(points)} Qdrant points.")
    return points
