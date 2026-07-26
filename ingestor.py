import os
from typing import List, Tuple
from pypdf import PdfReader

def load_pdfs(folder_path: str) -> List[Tuple[str, str]]:
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            filepath = os.path.join(folder_path, filename)
            reader = PdfReader(filepath)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            documents.append((filename, full_text))
            print(f"Loaded: {filename} ({len(reader.pages)} pages, {len(full_text)} chars)")
    return documents


def chunk_text(text: str, parent_size: int = 2000, child_size: int = 500, overlap: int = 50) -> List[dict]:
    chunks = []
    chunk_id = 0

    parent_start = 0
    while parent_start < len(text):
        parent_end = min(parent_start + parent_size, len(text))
        parent_chunk = text[parent_start:parent_end].strip()

        if parent_chunk:
            child_start = parent_start
            while child_start < parent_end:
                child_end = min(child_start + child_size, parent_end)
                child_chunk = text[child_start:child_end].strip()

                if len(child_chunk) > 50:  # skip tiny chunks
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "child_text": child_chunk,
                        "parent_text": parent_chunk,
                    })
                    chunk_id += 1

                # Move forward by child_size (no overlap inside parent)
                child_start = child_end

        # Move parent forward with no overlap to save memory
        parent_start = parent_end

    return chunks


def ingest_documents(folder_path: str = "./resources") -> List[dict]:
    documents = load_pdfs(folder_path)
    all_chunks = []

    for filename, text in documents:
        print(f"Chunking: {filename}")
        chunks = chunk_text(text)
        for chunk in chunks:
            chunk["source"] = filename
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks created")

    print(f"\nTotal chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = ingest_documents()
    print("\nSample chunk:")
    print("Child:", chunks[0]["child_text"][:200])
    print("Parent:", chunks[0]["parent_text"][:200])