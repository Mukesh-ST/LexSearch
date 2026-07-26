from sentence_transformers import SentenceTransformer
from typing import List

# BGE model produces 768-dim vectors (better quality than MiniLM's 384)
EMBEDDING_MODEL = SentenceTransformer("BAAI/bge-base-en-v1.5")

def embed_chunks(chunks: List[dict]) -> List[List[float]]:
    """Embed child chunks for storage in Pinecone"""
    texts = [chunk["child_text"] for chunk in chunks]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = EMBEDDING_MODEL.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        batch_size=32
    )
    print("Embedding complete.")
    return embeddings.tolist()

def embed_query(query: str) -> List[float]:
    """Embed a single user query"""
    # BGE models work better with this prefix for queries
    prefixed_query = f"Represent this sentence for searching relevant passages: {query}"
    embedding = EMBEDDING_MODEL.encode(prefixed_query, convert_to_numpy=True)
    return embedding.tolist()