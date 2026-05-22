"""
main.py — Entry point for the FastAPI backend

Think of this like the front door of your backend.
Every request from the frontend comes through here first.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from api.ingest import router as ingest_router

app = FastAPI(title="AI Dev OS", version="0.1.0")

# CORS: allows the frontend (running on localhost:3000)
# to talk to the backend (running on localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes — each file in /api handles a specific feature
app.include_router(chat_router, prefix="/api/chat")
app.include_router(ingest_router, prefix="/api/ingest")


@app.get("/health")
async def health():
    return {"status": "ok"}
