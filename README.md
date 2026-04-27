# RAG Module 5 — Intelligent Agent with Memory & Reasoning

Advanced AI agent combining RAG, session memory, persistent memory, and multi-step reasoning.

## What this module does

Extends Module 2's agent with:
- **Session memory** — remembers the full conversation during a session
- **Persistent memory** — saves important facts to Supabase across sessions
- **Source routing** — decides whether to search documents, memory, or both
- **Question decomposition** — breaks complex questions into sub-questions for better retrieval

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- OpenAI `gpt-4o-mini` + `text-embedding-3-small`
- Anthropic `claude-sonnet-4-5`
- Supabase (pgvector for RAG + PostgreSQL for memory)

## Structure

```
rag-module5/
├── config.py                      # centralized configuration
├── server.py                      # API entry point (port 8001)
├── setup_memory_table.sql         # run once in Supabase SQL Editor
├── requirements.txt
├── .env.example
└── src/
    ├── agent.py                   # main orchestrator
    ├── memory/
    │   ├── session_memory.py      # in-memory conversation history
    │   └── persistent_memory.py  # Supabase-backed long-term memory
    ├── reasoning/
    │   └── engine.py              # source routing + question decomposition
    └── api/
        └── routes.py              # FastAPI endpoints
```

## Setup

### 1. Install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# fill in your keys (same Supabase as Module 1)
```

### 3. Create the memory table in Supabase

In the Supabase dashboard → **SQL Editor** → run the contents of `setup_memory_table.sql`.

### 4. Start the server

```bash
python server.py
# runs on http://localhost:8001
```

## API Endpoints

### `POST /chat`
Send a message to the agent with session context.

```json
// Request
{
  "question": "What are the transfer pricing rules?",
  "session_id": "user-123",
  "provider": "claude"
}

// Response
{
  "question": "What are the transfer pricing rules?",
  "answer": "Based on the documents...",
  "session_id": "user-123",
  "provider": "claude",
  "model": "claude-sonnet-4-5",
  "sub_questions": ["What are transfer pricing rules?"],
  "chunks_used": 5,
  "sources_used": ["777-cropped.pdf"],
  "response_time_ms": 1823
}
```

### `GET /session/{session_id}`
Get full conversation history and persistent memories for a session.

### `DELETE /session/{session_id}`
Clear all memory for a session.

### `POST /session/{session_id}/memory`
Manually add a memory item.

```json
{
  "content": "User prefers answers in Portuguese",
  "memory_type": "preference",
  "importance": 3
}
```

### `GET /health`
```json
{ "status": "ok", "module": "rag-module5" }
```

## How memory works

```
User sends question
        ↓
Decompose into sub-questions (if complex)
        ↓
Decide source: RAG? Memory? Both?
        ↓
Retrieve chunks from Supabase (RAG)
Retrieve persistent memories from Supabase
        ↓
Build prompt with: history + memories + chunks + question
        ↓
Call LLM (Claude or OpenAI)
        ↓
Save answer to session history (in-memory)
Extract important facts → save to persistent memory (Supabase)
        ↓
Return response
```

## Part of a larger project

- Module 1 — Ingestion and RAG
- Module 2 — LLM Query Agent
- Module 3 — n8n Workflow Automation
- Module 4 — External Integrations (Google Sheets)
- **Module 5 — Agent with Memory & Reasoning** ← you are here
- Final project — Unified system
