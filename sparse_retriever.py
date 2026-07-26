from rank_bm25 import BM25Okapi
from typing import List
import re

def tokenize(text: str) -> List[str]:
    """Simple tokenizer — lowercase, remove punctuation, split by space"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()

class SparseRetriever:
    def __init__(self, chunks: List[dict]):
        """Build BM25 index from child chunks"""
        self.chunks = chunks
        tokenized = [tokenize(chunk["child_text"]) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized)
        print(f"BM25 index built with {len(chunks)} chunks")

    def search(self, query: str, top_k: int = 10) -> List[dict]:
        """Search using BM25 keyword matching"""
        tokenized_query = tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top_k indices sorted by score
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # only include relevant results
                results.append({
                    "chunk": self.chunks[idx],
                    "score": float(scores[idx]),
                    "type": "sparse"
                })
        return results