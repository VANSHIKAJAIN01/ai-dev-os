"""
rag/retriever.py — Combines embedder + vector_store to answer:
"What code is most relevant to this question?"

This is called every time the user sends a chat message.
"""
from rag.embedder import embed_query
from rag.vector_store import search


async def retrieve_context(query: str, project_id: str, top_k: int = 5) -> str:
    # Convert the user's question into a vector
    query_vector = await embed_query(query)

    # Find the most similar code chunks
    results = await search(project_id, query_vector, top_k)

    if not results:
        return "No relevant code context found."

    # Format chunks into a readable string for Claude's context
    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(f"[Chunk {i} — {r['file_path']} (relevance: {r['score']:.2f})]\n{r['text']}")

    return "\n\n---\n\n".join(formatted)
