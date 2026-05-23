"""
rag/embedder.py — Converts text into vectors (embeddings)

What is an embedding?
- A list of ~384 numbers that captures the MEANING of a piece of text
- Similar meanings → similar numbers → close together in vector space
- This is what enables semantic search

We use sentence-transformers (runs locally, completely free).
Alternative: OpenAI's text-embedding-3-small API (paid but better quality).
"""
from sentence_transformers import SentenceTransformer

# Load model once at startup (not on every request)
_model = SentenceTransformer("all-MiniLM-L6-v2")


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    embeddings = _model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


async def embed_query(text: str) -> list[float]:
    return _model.encode([text])[0].tolist()
