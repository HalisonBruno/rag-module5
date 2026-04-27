"""
FastAPI REST API for the memory agent.

Endpoints:
    POST /chat              — send a message (with session memory)
    GET  /sessions          — list active sessions
    GET  /session/{id}      — get session history
    DELETE /session/{id}    — clear session
    GET  /health            — health check
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from src.agent import ask
from src.memory.session_memory import (
    get_history, clear_session, list_sessions
)
from src.memory.persistent_memory import (
    get_memories, clear_memories, save_memory
)

app = FastAPI(
    title="RAG Agent API — Module 5",
    description="Intelligent agent with session memory, persistent memory, and multi-step reasoning",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)
    session_id: str = Field(..., min_length=1, example="user-123")
    provider: Optional[str] = Field(None, example="claude")


class ChatResponse(BaseModel):
    question: str
    answer: str
    session_id: str
    provider: str
    model: str
    sub_questions: list[str]
    chunks_used: int
    sources_used: list[str]
    response_time_ms: int


class MemoryRequest(BaseModel):
    content: str
    memory_type: str = "fact"
    importance: int = 1


@app.get("/health")
def health():
    return {"status": "ok", "module": "rag-module5"}


@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    """Send a message to the agent. Maintains conversation history per session_id."""
    try:
        return ask(
            question=body.question,
            session_id=body.session_id,
            provider=body.provider,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
def sessions():
    """List all active session IDs."""
    return {"sessions": list_sessions()}


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Get full conversation history for a session."""
    history = get_history(session_id)
    memories = get_memories(session_id)
    return {
        "session_id": session_id,
        "message_count": len(history),
        "history": history,
        "persistent_memories": memories,
    }


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Clear session memory (both in-memory and persistent)."""
    clear_session(session_id)
    deleted = clear_memories(session_id)
    return {"cleared": True, "persistent_memories_deleted": deleted}


@app.post("/session/{session_id}/memory")
def add_memory(session_id: str, body: MemoryRequest):
    """Manually add a memory item for a session."""
    success = save_memory(
        session_id=session_id,
        content=body.content,
        memory_type=body.memory_type,
        importance=body.importance,
    )
    return {"saved": success}
