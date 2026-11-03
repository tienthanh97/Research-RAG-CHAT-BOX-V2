import logging
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from qdrant_client.http.exceptions import ResponseHandlingException

from core.load_settings import load_settings
from core.schema import RetrievedDocument
from embedding.embed_texts import embed_texts
from vectorstore.qdrant import get_qdrant_client

settings = load_settings()
logger = logging.getLogger("retrieval")

RETRIEVAL_CONFIG = settings["retrieval"]
COLLECTION_NAME = settings["vector_database"]["collection_name"]
RETRIEVAL_TOP_K = RETRIEVAL_CONFIG.get("top_k", 5)
RETRIEVAL_SCORE_THRESHOLD = RETRIEVAL_CONFIG.get("score_threshold", 0.3)

def retrieve(query: str) -> list[RetrievedDocument]:
    if not query or not query.strip():
        logger.warning("Empty query received for retrieval.")
        return []

    try:
        client = get_qdrant_client()
        # Bước 1: Biến câu hỏi của người dùng thành vector
        vectors = embed_texts([query])
        
        if not vectors:
            logger.error("Failed to embed the query.")
            return []

        query_vector = vectors[0]

        # Bước 2: Thực hiện tìm kiếm trong Qdrant
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=RETRIEVAL_TOP_K,
            with_payload=True,
            score_threshold=RETRIEVAL_SCORE_THRESHOLD,
        )
        
        points:list[ScoredPoint]=response.points
        document:list[RetrievedDocument] = []

        for point in points:
            payload =point.payload or {}

            document.append(
                RetrievedDocument(
                    id=str(point.id),
                    score=point.score,
                    text=payload.get("text",""),
                    metadata={key:value for key,value in payload.items() if key !="text"}
                )
            )
            logger.info(f"Retrieved {len(document)} documents")
            return document

    except ResponseHandlingException as e:
        logger.error(f"Error during retrieval from Qdrant: {e}")
        raise ConnectionError(f"Cannot connect to vector database")
    except Exception as e:
        logger.error(f"Unexpected error during retrieval: {e}")
        return []
