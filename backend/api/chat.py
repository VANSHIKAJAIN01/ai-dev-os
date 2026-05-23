"""
api/chat.py — Handles chat messages from the frontend
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from rag.retriever import retrieve_context
from groq import Groq
import os

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ChatRequest(BaseModel):
    message: str
    project_id: str


@router.post("/")
async def chat(request: ChatRequest):
    context_chunks = await retrieve_context(request.message, request.project_id)

    prompt = f"""You are an AI assistant that helps developers understand and work with their codebase.

Here is the relevant code context retrieved for this question:

{context_chunks}

Use this context to give accurate, specific answers. If the context doesn't contain enough information, say so.

User question: {request.message}"""

    async def stream():
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in response:
            text = chunk.choices[0].delta.content
            if text:
                yield text

    return StreamingResponse(stream(), media_type="text/plain")
