"""
api/chat.py — Handles chat messages from the frontend

This is the core of Phase 1:
1. User sends a message
2. We search the vector DB for relevant code chunks (RAG)
3. We send message + chunks to Claude
4. We stream Claude's response back to the frontend token by token
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rag.retriever import retrieve_context
from anthropic import AsyncAnthropic
import os

router = APIRouter()
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class ChatRequest(BaseModel):
    message: str
    project_id: str


@router.post("/")
async def chat(request: ChatRequest):
    # Step 1: Find relevant code chunks from vector DB
    context_chunks = await retrieve_context(request.message, request.project_id)

    # Step 2: Build the prompt with context injected
    system_prompt = f"""You are an AI assistant that helps developers understand and work with their codebase.

Here is the relevant code context retrieved for this question:

{context_chunks}

Use this context to give accurate, specific answers. If the context doesn't contain enough information, say so.
"""

    # Step 3: Stream Claude's response back
    async def stream():
        async with client.messages.stream(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": request.message}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    return StreamingResponse(stream(), media_type="text/plain")
