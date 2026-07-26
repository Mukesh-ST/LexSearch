import os
from dotenv import load_dotenv
from pinecone import Pinecone
from ingestor import ingest_documents
from embedder import embed_chunks

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def store_in_pinecone(chunks, embeddings):
    """Store chunks and their embeddings in Pinecone"""
    vectors_to_upsert = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors_to_upsert.append({
            "id": chunk["id"],
            "values": embedding,
            "metadata": {
                "child_text": chunk["child_text"],
                "parent_text": chunk["parent_text"],
                "source": chunk["source"]
            }
        })

    # Upsert in batches of 100
    batch_size = 100
    total_batches = len(vectors_to_upsert) // batch_size + 1
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i // batch_size + 1}/{total_batches}")

    print(f"\nTotal vectors stored in Pinecone: {len(vectors_to_upsert)}")


def run():
    print("=== LexSearch Ingestion Pipeline ===\n")

    # Step 1 — Load and chunk PDFs
    print("Step 1: Loading and chunking PDFs...")
    chunks = ingest_documents("./resources")

    # Step 2 — Generate embeddings
    print("\nStep 2: Generating embeddings...")
    embeddings = embed_chunks(chunks)

    # Step 3 — Store in Pinecone
    print("\nStep 3: Storing in Pinecone...")
    store_in_pinecone(chunks, embeddings)

    print("\n=== Ingestion Complete ===")
    print(f"Total chunks ingested: {len(chunks)}")
    print("You can now run: streamlit run app.py")


if __name__ == "__main__":
    run()