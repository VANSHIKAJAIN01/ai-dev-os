"""
rag/vector_store.py — Talks to Qdrant (our vector database)

Two main operations:
1. upsert_chunks: store embeddings (called during ingestion)
2. search: find similar chunks (called during chat)

Qdrant organizes data into "collections" — we use one per project.
Each point in a collection has:
- an id (unique number)
- a vector (the embedding)
- a payload (the original text + metadata)
"""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
import uuid

client = AsyncQdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))

VECTOR_SIZE = 384  # size for all-MiniLM-L6-v2 model


async def ensure_collection(project_id: str):
    """Create the collection if it doesn't exist yet."""
    collections = await client.get_collections()
    names = [c.name for c in collections.collections]

    if project_id not in names:
        await client.create_collection(
            collection_name=project_id,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


async def upsert_chunks(project_id: str, chunks: list[dict], embeddings: list[list[float]]):
    await ensure_collection(project_id)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk["text"], **chunk["metadata"]}
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    await client.upsert(collection_name=project_id, points=points)


async def search(project_id: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
    results = await client.search(
        collection_name=project_id,
        query_vector=query_vector,
        limit=top_k,
    )
    return [{"text": r.payload["text"], "file_path": r.payload.get("file_path", ""), "score": r.score}
            for r in results]
