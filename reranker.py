from sentence_transformers import CrossEncoder
from typing import List

# Cross-encoder model for re-ranking — runs locally, free
RERANKER_MODEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, results: List[dict], top_k: int = 5) -> List[dict]:
    """
    Re-rank hybrid search results using a cross-encoder.
    Cross-encoder looks at query + chunk together (more accurate than embeddings alone).
    """
    if not results:
        return []

    # Pair query with each chunk's child text
    pairs = [[query, result["chunk"]["child_text"]] for result in results]

    # Score each pair
    scores = RERANKER_MODEL.predict(pairs)

    # Attach scores and sort
    for i, result in enumerate(results):
        result["rerank_score"] = float(scores[i])

    reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_k]