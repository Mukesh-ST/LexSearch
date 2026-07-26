import streamlit as st
from ingestor import ingest_documents
from pipeline import process_query, memory

st.set_page_config(page_title="LexSearch", page_icon="⚖️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg-from: #0F0C29;
    --bg-mid: #302B63;
    --bg-to: #24243E;
    --card-bg: rgba(255,255,255,0.05);
    --card-border: rgba(255,255,255,0.12);
    --user-bg: rgba(99,102,241,0.2);
    --user-border: rgba(99,102,241,0.4);
    --accent: #818CF8;
    --accent2: #C084FC;
    --gold: #FBBF24;
    --text-primary: #F1F5F9;
    --text-muted: #94A3B8;
    --hairline: rgba(255,255,255,0.08);
    --glow: 0 0 40px rgba(129,140,248,0.15);
}

* { box-sizing: border-box; }

.stApp {
    background: linear-gradient(135deg, var(--bg-from) 0%, var(--bg-mid) 50%, var(--bg-to) 100%);
    font-family: 'Space Grotesk', sans-serif;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }

/* ---- Animated background orbs ---- */
.stApp::before {
    content: '';
    position: fixed;
    top: -20%;
    left: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(129,140,248,0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    bottom: -20%;
    right: -10%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(192,132,252,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}

/* ---- Letterhead ---- */
.letterhead {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid var(--hairline);
    margin-bottom: 2rem;
    position: relative;
}
.letterhead .seal {
    display: inline-flex; align-items: center; justify-content: center;
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #818CF8, #C084FC);
    border-radius: 14px;
    color: white; font-size: 1.3rem;
    margin-right: 1rem; vertical-align: middle;
    box-shadow: 0 8px 24px rgba(129,140,248,0.4),
                0 2px 4px rgba(0,0,0,0.3),
                inset 0 1px 0 rgba(255,255,255,0.2);
    transform: perspective(100px) rotateX(5deg);
}
.letterhead h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 2rem;
    background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #FBBF24 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: inline; vertical-align: middle;
    letter-spacing: -0.5px;
}
.letterhead p {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem; color: var(--text-muted);
    margin: 0.5rem 0 0 4rem;
    letter-spacing: 1.5px; text-transform: uppercase;
}

/* ---- Chat bubbles ---- */
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid var(--card-border);
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.2),
                inset 0 1px 0 rgba(255,255,255,0.08);
    position: relative;
}
[aria-label="Chat message from assistant"] {
    background: var(--card-bg);
}
[aria-label="Chat message from user"] {
    background: var(--user-bg);
    border-color: var(--user-border);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] .stMarkdown,
[data-testid="stChatMessage"] div {
    background: transparent !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: var(--text-primary) !important;
    font-size: 0.95rem; line-height: 1.7;
}
[data-testid="stChatMessage"] strong {
    color: var(--accent) !important;
}

/* ---- Rewrite tag ---- */
.rewrite-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--gold);
    background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.3);
    border-radius: 6px;
    padding: 4px 10px;
    display: inline-block;
    margin-bottom: 0.75rem;
    letter-spacing: 0.5px;
}

/* ---- Expanders ---- */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--hairline);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    margin-top: 0.6rem;
    backdrop-filter: blur(8px);
}
[data-testid="stExpander"] summary {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--accent) !important;
    text-transform: uppercase; letter-spacing: 1px;
}
[data-testid="stExpander"] p,
[data-testid="stExpander"] div {
    font-size: 0.82rem;
    color: var(--text-muted) !important;
    line-height: 1.55;
    background: transparent !important;
}

/* ---- Chat input ---- */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.2),
                inset 0 1px 0 rgba(255,255,255,0.08);
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(129,140,248,0.2),
                0 4px 24px rgba(0,0,0,0.2) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    background: transparent !important;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.8);
    border-right: 1px solid var(--hairline);
    backdrop-filter: blur(20px);
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--accent) !important;
    text-transform: uppercase; letter-spacing: 1.5px;
    font-weight: 400;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] label {
    color: var(--text-muted) !important;
    font-size: 0.82rem;
}
.stButton button {
    background: linear-gradient(135deg, rgba(129,140,248,0.15), rgba(192,132,252,0.15));
    border: 1px solid var(--card-border);
    color: var(--text-primary);
    border-radius: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.stButton button:hover {
    border-color: var(--accent);
    background: linear-gradient(135deg, rgba(129,140,248,0.25), rgba(192,132,252,0.25));
    box-shadow: 0 4px 16px rgba(129,140,248,0.25);
    transform: translateY(-1px);
}

/* ---- Empty state ---- */
.empty-state {
    text-align: center;
    padding: 3.5rem 1rem;
}
.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 20px rgba(129,140,248,0.5));
}
.empty-state h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818CF8, #C084FC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}
.empty-state p {
    font-size: 0.88rem;
    line-height: 1.8;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
}
.example {
    display: inline-block;
    background: rgba(129,140,248,0.1);
    border: 1px solid rgba(129,140,248,0.25);
    border-radius: 20px;
    padding: 6px 16px;
    margin: 4px;
    font-size: 0.8rem;
    color: var(--accent);
    cursor: pointer;
    transition: all 0.2s ease;
}
.example:hover {
    background: rgba(129,140,248,0.2);
    box-shadow: 0 4px 12px rgba(129,140,248,0.2);
}

hr { border-color: var(--hairline) !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- HEADER -----------------------------
st.markdown("""
<div class="letterhead">
    <span class="seal">⚖</span><h1>LexSearch</h1>
    <p>Indian Legal Document Research · AI-Powered · RTI · IT Act</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------- LOAD CHUNKS (cached) -----------------------------
@st.cache_resource
def load_chunks():
    return ingest_documents("./resources")

chunks = load_chunks()

# ----------------------------- STATE -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------- SIDEBAR -----------------------------
with st.sidebar:
    st.markdown("### Settings")
    top_k = st.slider("Chunks retrieved", min_value=2, max_value=10, value=5)
    show_rewrite = st.toggle("Show rewritten query", value=True)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        memory.clear()
        st.rerun()
    st.divider()
    st.markdown("### Documents Loaded")
    st.caption("📄 RTI Act Handbook 2021")
    st.caption("📄 IT Act 2000")
    st.divider()
    st.caption("Embeddings · BAAI/bge-base-en-v1.5")
    st.caption("Retrieval · Hybrid Search + BM25 + RRF")
    st.caption("Reranking · cross-encoder/ms-marco-MiniLM")
    st.caption("Generation · Groq · Llama 3.3 70B")
    st.caption("Vector Store · Pinecone")

# ----------------------------- EMPTY STATE -----------------------------
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">⚖️</div>
        <h3>Ask anything about Indian law</h3>
        <p>Hybrid search · Re-ranking · Llama 3.3 70B<br>
        RTI Act 2005 · IT Act 2000</p>
        <div>
            <span class="example">Penalties for hacking under IT Act?</span>
            <span class="example">Time limit for RTI response?</span>
            <span class="example">Who is a Public Information Officer?</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------- CHAT HISTORY -----------------------------
for message in st.session_state.messages:
    avatar = "⚖️" if message["role"] == "assistant" else "🙂"
    with st.chat_message(message["role"], avatar=avatar):
        if message["role"] == "assistant" and message.get("rewritten_query") and show_rewrite:
            st.markdown(
                f'<div class="rewrite-tag">🔍 Rewritten: {message["rewritten_query"]}</div>',
                unsafe_allow_html=True
            )
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📜 Legal sources cited"):
                for source in message["sources"]:
                    st.markdown(f"**§** {source}")
        if message["role"] == "assistant" and message.get("context_chunks"):
            with st.expander("🔎 Retrieved context chunks"):
                for i, chunk in enumerate(message["context_chunks"][:3], 1):
                    st.markdown(f"**Chunk {i}** — {chunk['chunk']['source']}")
                    st.text(chunk["chunk"]["child_text"][:300] + "...")

# ----------------------------- CHAT INPUT -----------------------------
if user_query := st.chat_input("Ask about RTI, IT Act, or any loaded legal document..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="🙂"):
        st.markdown(user_query)

    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Searching legal documents..."):
            try:
                result = process_query(user_query, chunks, top_k=top_k)
                if show_rewrite:
                    st.markdown(
                        f'<div class="rewrite-tag">🔍 Rewritten: {result["rewritten_query"]}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown(result["answer"])
                if result["sources"]:
                    with st.expander("📜 Legal sources cited"):
                        for source in result["sources"]:
                            st.markdown(f"**§** {source}")
                if result["context_chunks"]:
                    with st.expander("🔎 Retrieved context chunks"):
                        for i, chunk in enumerate(result["context_chunks"][:3], 1):
                            st.markdown(f"**Chunk {i}** — {chunk['chunk']['source']}")
                            st.text(chunk["chunk"]["child_text"][:300] + "...")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "rewritten_query": result["rewritten_query"],
                    "sources": result["sources"],
                    "context_chunks": result["context_chunks"]
                })
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", "content": error_msg
                })