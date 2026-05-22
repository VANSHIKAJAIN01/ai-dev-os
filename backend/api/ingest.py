"""
api/ingest.py — Handles ingesting a GitHub repo into the vector DB

Flow:
1. User provides a GitHub repo URL
2. We fetch all code files from the repo
3. We split them into small chunks
4. We convert chunks to vectors (embeddings)
5. We store vectors in Qdrant

After this, the repo is "searchable" by meaning.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from rag.ingester import ingest_github_repo

router = APIRouter()


class IngestRequest(BaseModel):
    repo_url: str    # e.g. "https://github.com/user/repo"
    project_id: str  # used to namespace the vectors in Qdrant


@router.post("/")
async def ingest(request: IngestRequest):
    result = await ingest_github_repo(request.repo_url, request.project_id)
    return result
