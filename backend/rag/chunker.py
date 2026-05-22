"""
rag/chunker.py — Splits large files into smaller chunks

Why chunk?
- Claude has a context window limit (can't read the whole repo at once)
- Vector search works better on small, focused pieces of text
- We want to retrieve only the RELEVANT part, not the whole file

Strategy: split by lines with overlap
- chunk_size: how many characters per chunk
- overlap: how many characters to repeat between chunks
  (overlap helps preserve context at chunk boundaries)
"""


def chunk_text(text: str, metadata: dict, chunk_size: int = 1500, overlap: int = 200) -> list[dict]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():  # skip empty chunks
            chunks.append({
                "text": chunk,
                "metadata": {**metadata, "chunk_index": len(chunks)}
            })

        start += chunk_size - overlap  # move forward with overlap

    return chunks
