import os
from groq import Groq
from dotenv import load_dotenv
from typing import List

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query: str, context_chunks: List[dict], conversation_history: str = "") -> str:
    """
    Generate answer using Groq LLM with:
    - Retrieved context chunks (parent text for full context)
    - Conversation history for multi-turn memory
    """

    # Build context from parent chunks (full surrounding context)
    context = "\n\n---\n\n".join([
        f"Source: {chunk['chunk']['source']}\n{chunk['chunk']['parent_text']}"
        for chunk in context_chunks
    ])

    # Build system prompt
    system_prompt = """You are LexSearch, an expert legal research assistant specializing in Indian law.
Answer questions accurately based only on the provided legal document context.
Always mention the relevant Act or section when answering.
If the context does not contain enough information, clearly say so.
Do not make assumptions beyond what is stated in the documents.
Be precise, clear and structured in your answers."""

    # Build user message with history + context + query
    user_message = ""
    if conversation_history:
        user_message += f"Previous conversation:\n{conversation_history}\n\n"

    user_message += f"""Legal Document Context:
{context}

Current Question: {query}

Provide a clear, accurate answer based on the context above."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()