# ⚖️ LexSearch — Legal Document Research Assistant

An AI-powered legal research assistant that answers questions about Indian legal documents using an advanced Retrieval-Augmented Generation (RAG) pipeline with hybrid search, re-ranking, query rewriting, and conversation memory.

---

## 📸 Demo

Ask questions like:

- *"What is the time limit to respond to an RTI request?"*
- *"What are the penalties for hacking under IT Act 2000?"*
- *"What is the appeal process under RTI Act?"*

---

## 🧠 Architecture

**Ingestion Pipeline (runs once)**

PDF Documents → PyPDF Extraction → Parent-Child Chunking → BGE Embeddings (local) → Pinecone Vector Store (894 vectors)

**Query Pipeline (every question)**

User Question → Query Rewriting (Groq) → Hybrid Search (Dense Pinecone + Sparse BM25 + RRF Fusion) → Cross-Encoder Re-ranking → Parent Context Retrieval → Conversation Memory → Groq Llama 3.3 70B → Answer + Sources

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| PDF Extraction | PyPDF | Extract text from legal PDFs |
| Chunking | Parent-Child (custom) | Small chunks for search, large for context |
| Dense Embeddings | BAAI/bge-base-en-v1.5 (local) | 768-dim semantic vectors |
| Sparse Search | BM25 (rank-bm25) | Exact keyword matching |
| Hybrid Fusion | Reciprocal Rank Fusion | Combines dense + sparse scores |
| Vector Database | Pinecone | Store and search 768-dim vectors |
| Re-ranking | cross-encoder/ms-marco-MiniLM | Precision re-scoring of results |
| Query Rewriting | Groq · Llama 3.3 70B | Converts vague queries to legal terms |
| LLM | Groq · Llama 3.3 70B | Context-grounded answer generation |
| Memory | Custom MemoryManager | Multi-turn conversation history |
| Evaluation | LLM-as-Judge (Groq) | Faithfulness, relevancy, precision scoring |
| UI | Streamlit | Interactive chat interface |

---

## 📁 Project Structure

| File | Purpose |
|------|---------|
| app.py | Streamlit chat UI |
| dataprocessor.py | One-time ingestion pipeline |
| ingestor.py | PDF loading + parent-child chunking |
| embedder.py | BGE local embeddings |
| sparse_retriever.py | BM25 keyword search |
| hybrid_retriever.py | Dense + sparse + RRF fusion |
| reranker.py | Cross-encoder re-ranking |
| query_rewriter.py | LLM-based query rewriting |
| memory_manager.py | Conversation memory |
| llm.py | Groq LLM answer generation |
| pipeline.py | Full query orchestration |
| evaluator.py | Custom evaluation script |

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.10+
- Pinecone account (free) — console.pinecone.io
- Groq account (free) — console.groq.com

### 1. Clone the repository

```
git clone https://github.com/Mukesh-ST/LexSearch.git
cd LexSearch
```

### 2. Create and activate virtual environment

```
python -m venv .myenv
```

Windows:
```
.myenv\Scripts\activate
```

Mac/Linux:
```
source .myenv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=lexsearch
GROQ_API_KEY=your_groq_key
```

### 5. Create Pinecone Index

- Dimension: 768
- Metric: cosine
- Name: lexsearch

### 6. Add legal PDFs to resources/ folder

### 7. Run ingestion (once)

```
python dataprocessor.py
```

### 8. Launch chatbot

```
streamlit run app.py
```

Opens at http://localhost:8501

---

## 📊 Evaluation Results

Evaluated using LLM-as-Judge methodology with Groq Llama 3.3 70B across 10 legal test questions:

| Metric | Score |
|--------|-------|
| Answer Relevancy | 0.85 |
| Faithfulness | 0.57 |
| Context Precision | 0.49 |
| Overall | 0.64 |

---

## 🔑 Key Design Decisions

**Why parent-child chunking?**

Small chunks (500 chars) give precise search results. But sending only 500 chars to the LLM loses surrounding context. Parent-child solves this — search small, answer with large (2000 chars).

**Why hybrid search?**

Dense search alone misses exact legal terms like "Section 66" or "PIO". BM25 alone misses semantic meaning. Together they cover both.

**Why re-ranking?**

Embedding similarity is approximate. Cross-encoder looks at query and chunk together — much more accurate. Used after hybrid search to reorder only top candidates.

**Why query rewriting?**

Users ask vague questions. LLM rewrites them into precise legal search queries before retrieval, significantly improving what Pinecone returns.

**Why local embeddings?**

Zero cost, zero rate limits, works offline. BGE-base produces 768-dim vectors — higher quality for legal domain retrieval.

---

## 🚀 Features

- Multi-turn conversation with memory (last 5 turns)
- Query rewriting — vague questions converted to precise legal queries
- Hybrid search — dense semantic + BM25 keyword + RRF fusion
- Cross-encoder re-ranking for precision
- Source citations — exact document and chunk shown
- Built-in evaluation with faithfulness and relevancy scoring
- Local embeddings — no API dependency for embedding

---

## 📦 Requirements

- pypdf
- pdfplumber
- sentence-transformers
- rank-bm25
- pinecone
- groq
- streamlit
- python-dotenv

---

## 🙋 Use Cases

- Legal researchers querying Indian acts and regulations
- Citizens understanding their RTI and IT Act rights
- Law students studying specific sections and penalties
- Organizations building legal compliance tools

---

## 📌 Future Improvements

- Add more Indian legal documents (IPC, Consumer Protection Act)
- Improve IT Act coverage with comprehensive PDFs
- Deploy on Streamlit Cloud for public access
- Add citation with exact section numbers
- Implement RAGAS evaluation framework

---

## 👤 Author

**Mukesh S T**

- GitHub: [@Mukesh-ST](https://github.com/Mukesh-ST)

---

## 📄 License

This project is open source and available under the MIT License.
