import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def rewrite_query(query: str) -> str:
    """
    Rewrites a vague user question into a precise legal search query using Groq.
    Example:
        Input:  "what happens if someone leaks my data?"
        Output: "penalties for unauthorized disclosure of personal data IT Act 2000"
    """
    prompt = f"""You are a legal search query optimizer. 
Rewrite the following user question into a precise, keyword-rich legal search query.
Keep it under 20 words. Return only the rewritten query, nothing else.

User question: {query}
Rewritten query:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=50
    )

    rewritten = response.choices[0].message.content.strip()
    print(f"Original query: {query}")
    print(f"Rewritten query: {rewritten}")
    return rewritten