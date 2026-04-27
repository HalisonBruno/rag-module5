"""
Main agent with memory and orchestration.
Combines RAG, session memory, persistent memory, and reasoning.
"""
import os
import time
from openai import OpenAI
from anthropic import Anthropic
from supabase import create_client

from config import (
    DEFAULT_PROVIDER, OPENAI_API_KEY, ANTHROPIC_API_KEY,
    OPENAI_CHAT_MODEL, ANTHROPIC_CHAT_MODEL,
    OPENAI_EMBEDDING_MODEL, EMBEDDING_DIMENSIONS,
    SUPABASE_URL, SUPABASE_SERVICE_KEY,
    RAG_TOP_K, RAG_THRESHOLD
)
from src.memory.session_memory import (
    add_message, get_messages_for_llm, get_history
)
from src.memory.persistent_memory import (
    save_memory, format_memories_for_prompt
)
from src.reasoning.engine import (
    decide_source, decompose_question, extract_facts_to_remember
)

_openai = OpenAI(api_key=OPENAI_API_KEY)
_anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on document excerpts and conversation history.

Rules:
- Answer based on the provided context (documents and/or memory)
- If context is insufficient, say clearly: "I could not find this information in the available documents."
- Do not invent information
- Be objective and concise
- Answer in the same language the user used
- When referencing documents, mention the source filename"""


def _embed(text: str) -> list[float]:
    response = _openai.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=[text],
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding


def _rag_search(query: str, top_k: int = RAG_TOP_K, threshold: float = RAG_THRESHOLD) -> list[dict]:
    embedding = _embed(query)
    result = _supabase.rpc(
        "search_documents",
        {"query_embedding": embedding, "match_threshold": 0.1, "match_count": top_k}
    ).execute()
    print(f"[debug] RAG search returned {len(result.data or [])} chunks")
    return result.data or []
    embedding = _embed(query)
    result = _supabase.rpc(
        "search_documents",
        {"query_embedding": embedding, "match_threshold": threshold, "match_count": top_k}
    ).execute()
    return result.data or []


def _build_context(chunks: list[dict], persistent_memory: str, question: str) -> str:
    parts = []

    if persistent_memory:
        parts.append(persistent_memory)

    if chunks:
        excerpts = []
        for i, c in enumerate(chunks, 1):
            filename = c.get("metadata", {}).get("filename", "unknown")
            score = c.get("similarity", 0)
            excerpts.append(f"[Excerpt {i} | {filename} | score: {score:.2f}]\n{c['content']}")
        parts.append("Document excerpts:\n\n" + "\n\n---\n\n".join(excerpts))

    parts.append(f"Question: {question}")
    return "\n\n".join(parts)


def _call_llm(session_id: str, context: str, provider: str) -> str:
    history = get_messages_for_llm(session_id)
    user_message = {"role": "user", "content": context}

    if provider == "openai":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [user_message]
        response = _openai.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    else:
        messages = history + [user_message]
        response = _anthropic.messages.create(
            model=ANTHROPIC_CHAT_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text.strip()


def ask(
    question: str,
    session_id: str,
    provider: str | None = None,
) -> dict:
    """
    Main agent function with full memory and reasoning.

    Args:
        question:   user's question
        session_id: unique session identifier (user/conversation ID)
        provider:   "openai" | "claude" | None (uses DEFAULT_PROVIDER)

    Returns:
        {
            "question":     str,
            "answer":       str,
            "session_id":   str,
            "provider":     str,
            "model":        str,
            "sub_questions": list,
            "chunks_used":  int,
            "sources_used": list,
            "response_time_ms": int
        }
    """
    start = time.time()
    selected_provider = (provider or DEFAULT_PROVIDER).lower()
    model = OPENAI_CHAT_MODEL if selected_provider == "openai" else ANTHROPIC_CHAT_MODEL

    # Step 1: decompose question if complex
    sub_questions = decompose_question(question)

    # Step 2: decide sources
    has_memory = bool(get_history(session_id))
    routing = decide_source(question, has_memory)

    # Step 3: retrieve context
    all_chunks = []
    if routing.get("use_rag"):
        for sub_q in sub_questions:
            chunks = _rag_search(sub_q)
            # deduplicate by chunk id
            seen_ids = {c["id"] for c in all_chunks}
            all_chunks.extend([c for c in chunks if c["id"] not in seen_ids])

    persistent_ctx = ""
    if routing.get("use_memory"):
        persistent_ctx = format_memories_for_prompt(session_id)

    # Step 4: build context and call LLM
    context = _build_context(all_chunks, persistent_ctx, question)
    add_message(session_id, "user", question)

    answer = _call_llm(session_id, context, selected_provider)
    add_message(session_id, "assistant", answer)

    # Step 5: extract and save important facts to persistent memory
    facts = extract_facts_to_remember(question, answer)
    for fact in facts:
        save_memory(session_id, fact, memory_type="fact", importance=2)

    elapsed_ms = int((time.time() - start) * 1000)
    sources = list({c.get("metadata", {}).get("filename", "unknown") for c in all_chunks})

    return {
        "question":         question,
        "answer":           answer,
        "session_id":       session_id,
        "provider":         selected_provider,
        "model":            model,
        "sub_questions":    sub_questions,
        "chunks_used":      len(all_chunks),
        "sources_used":     sources,
        "response_time_ms": elapsed_ms,
    }
