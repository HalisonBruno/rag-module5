"""
Persistent memory — saves important facts and summaries to Supabase.
Survives server restarts and persists across sessions.

Supabase table required (run once in SQL Editor):

    create table if not exists agent_memory (
        id          bigserial primary key,
        session_id  text not null,
        memory_type text not null,  -- 'fact' | 'summary' | 'preference'
        content     text not null,
        importance  int default 1,  -- 1-5, higher = more important
        created_at  timestamptz default now()
    );

    create index on agent_memory (session_id);
"""
from datetime import datetime
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY, PERSISTENT_MEMORY_MAX_ITEMS

_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
MEMORY_TABLE = "agent_memory"


def save_memory(
    session_id: str,
    content: str,
    memory_type: str = "fact",
    importance: int = 1
) -> bool:
    """
    Saves a memory item to Supabase.

    Args:
        session_id:   identifies the user/session
        content:      the memory content to save
        memory_type:  'fact' | 'summary' | 'preference'
        importance:   1-5, higher items are prioritized in retrieval
    """
    try:
        _client.table(MEMORY_TABLE).insert({
            "session_id":  session_id,
            "memory_type": memory_type,
            "content":     content,
            "importance":  importance,
        }).execute()
        return True
    except Exception as e:
        print(f"[persistent_memory] Failed to save: {e}")
        return False


def get_memories(session_id: str, memory_type: str | None = None) -> list[dict]:
    """
    Retrieves memory items for a session, ordered by importance.

    Args:
        session_id:   the session to retrieve memories for
        memory_type:  optional filter — 'fact' | 'summary' | 'preference'
    """
    try:
        query = (
            _client.table(MEMORY_TABLE)
            .select("*")
            .eq("session_id", session_id)
            .order("importance", desc=True)
            .limit(PERSISTENT_MEMORY_MAX_ITEMS)
        )
        if memory_type:
            query = query.eq("memory_type", memory_type)

        result = query.execute()
        return result.data or []
    except Exception as e:
        print(f"[persistent_memory] Failed to retrieve: {e}")
        return []


def format_memories_for_prompt(session_id: str) -> str:
    """
    Returns a formatted string of memories ready to inject into a prompt.
    """
    memories = get_memories(session_id)
    if not memories:
        return ""

    lines = ["[Known facts about this user/session:]"]
    for m in memories:
        lines.append(f"- [{m['memory_type']}] {m['content']}")
    return "\n".join(lines)


def clear_memories(session_id: str) -> int:
    """Deletes all memories for a session. Returns count deleted."""
    try:
        result = (
            _client.table(MEMORY_TABLE)
            .delete()
            .eq("session_id", session_id)
            .execute()
        )
        return len(result.data)
    except Exception as e:
        print(f"[persistent_memory] Failed to clear: {e}")
        return 0
