"""
rag/ingester.py — Fetches a GitHub repo and stores it in the vector DB

Step by step:
1. Call GitHub API to get all files in the repo
2. Download each file's content
3. Split content into chunks (chunking)
4. Create an embedding for each chunk (embedding)
5. Store embedding + original text in Qdrant
"""
import httpx
import os
from rag.chunker import chunk_text
from rag.embedder import embed_texts
from rag.vector_store import upsert_chunks


async def ingest_github_repo(repo_url: str, project_id: str) -> dict:
    # Parse owner/repo from URL like https://github.com/user/repo
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1].replace(".git", "")

    files = await fetch_repo_files(owner, repo)

    all_chunks = []
    for file in files:
        chunks = chunk_text(
            text=file["content"],
            metadata={"file_path": file["path"], "repo": repo, "project_id": project_id}
        )
        all_chunks.extend(chunks)

    # Embed all chunks in batches
    texts = [c["text"] for c in all_chunks]
    embeddings = await embed_texts(texts)

    # Store in Qdrant
    await upsert_chunks(project_id, all_chunks, embeddings)

    return {"status": "ok", "chunks_ingested": len(all_chunks)}


async def fetch_repo_files(owner: str, repo: str) -> list[dict]:
    """Recursively fetch all code files from a GitHub repo."""
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    files = []

    async with httpx.AsyncClient() as client:
        # Get the file tree (recursive=1 gets everything at once)
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1",
            headers=headers
        )
        tree = resp.json().get("tree", [])

        for item in tree:
            # Only process code files, skip binaries and large files
            if item["type"] == "blob" and is_code_file(item["path"]) and item.get("size", 0) < 100_000:
                content_resp = await client.get(item["url"], headers=headers)
                content_data = content_resp.json()
                if content_data.get("encoding") == "base64":
                    import base64
                    content = base64.b64decode(content_data["content"]).decode("utf-8", errors="ignore")
                    files.append({"path": item["path"], "content": content})

    return files


def is_code_file(path: str) -> bool:
    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".rs",
                       ".cpp", ".c", ".cs", ".rb", ".php", ".swift", ".kt", ".md"}
    return any(path.endswith(ext) for ext in code_extensions)
