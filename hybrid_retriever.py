from typing import List
from embedder import embed_query
from sparse_retriever import SparseRetriever

def reciprocal_rank_fusion(dense_results: List[dict], sparse_results: List[dict], k: int = 60) -> List[dict]:
    """
    Combine dense and sparse results using Reciprocal Rank Fusion (RRF).
    RRF score = 1/(k + rank) for each result, summed across both lists.
    """
    scores = {}

    for rank, result in enumerate(dense_results):
        chunk_id = result["chunk"]["id"]
        scores[chunk_id] = scores.get(chunk_id, {"score": 0, "chunk": result["chunk"]})
        scores[chunk_id]["score"] += 1 / (k + rank + 1)

    for rank, result in enumerate(sparse_results):
        chunk_id = result["chunk"]["id"]
        if chunk_id not in scores:
            scores[chunk_id] = {"score": 0, "chunk": result["chunk"]}
        scores[chunk_id]["score"] += 1 / (k + rank + 1)

    # Sort by combined RRF score
    fused = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    return fused


class HybridRetriever:
    def __init__(self, chunks: List[dict], index):
        """
        chunks: all document chunks (for BM25)
        index: Pinecone index (for dense search)
        """
        self.chunks = chunks
        self.index = index
        self.sparse = SparseRetriever(chunks)

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        # 1. Dense search via Pinecone
        query_vector = embed_query(query)
        dense_response = self.index.query(
            vector=query_vector,
            top_k=top_k * 2,
            include_metadata=True
        )
        dense_results = [
            {
                "chunk": {
                    "id": match.id,
                    "child_text": match.metadata.get("child_text", ""),
                    "parent_text": match.metadata.get("parent_text", ""),
                    "source": match.metadata.get("source", "")
                },
                "score": match.score,
                "type": "dense"
            }
            for match in dense_response.matches
        ]

        # 2. Sparse search via BM25
        sparse_results = self.sparse.search(query, top_k=top_k * 2)

        # 3. Fuse both using RRF
        fused_results = reciprocal_rank_fusion(dense_results, sparse_results)

        return fused_results[:top_k]