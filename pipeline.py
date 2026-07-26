import os
from dotenv import load_dotenv
from pinecone import Pinecone
from ingestor import ingest_documents
from embedder import embed_chunks, embed_query
from hybrid_retriever import HybridRetriever
from reranker import rerank
from query_rewriter import rewrite_query
from memory_manager import MemoryManager
from llm import generate_answer
from typing import List

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

# Global memory manager
memory = MemoryManager(max_turns=5)

def process_query(query: str, chunks: List[dict], top_k: int = 5) -> dict:
    """
    Full RAG pipeline:
    1. Rewrite query
    2. Hybrid search (dense + sparse)
    3. Rerank results
    4. Generate answer with memory
    """

    # Step 1 — Rewrite query for better retrieval
    rewritten_query = rewrite_query(query)

    # Step 2 — Hybrid search
    retriever = HybridRetriever(chunks, index)
    hybrid_results = retriever.search(rewritten_query, top_k=top_k * 2)

    # Step 3 — Rerank
    reranked_results = rerank(rewritten_query, hybrid_results, top_k=top_k)

    # Step 4 — Get conversation history
    conversation_history = memory.get_history_as_text()

    # Step 5 — Generate answer
    answer = generate_answer(rewritten_query, reranked_results, conversation_history)

    # Step 6 — Update memory
    memory.add_user_message(query)
    memory.add_assistant_message(answer)

    # Return answer + sources for UI
    sources = list(set([
        result["chunk"]["source"]
        for result in reranked_results
        if result["chunk"]["source"]
    ]))

    return {
        "original_query": query,
        "rewritten_query": rewritten_query,
        "answer": answer,
        "sources": sources,
        "context_chunks": reranked_results
    }