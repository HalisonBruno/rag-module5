"""
Session memory — keeps conversation history in memory for the duration of a session.
Each session_id has its own independent message history.
"""
from collections import defaultdict
from datetime import datetime
from config import SESSION_MEMORY_MAX_TURNS


# { session_id: [ {role, content, timestamp}, ... ] }
_sessions: dict[str, list[dict]] = defaultdict(list)


def add_message(session_id: str, role: str, content: str) -> None:
    """Adds a message to the session history."""
    _sessions[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    # keep only the last N turns to avoid token overflow
    if len(_sessions[session_id]) > SESSION_MEMORY_MAX_TURNS * 2:
        _sessions[session_id] = _sessions[session_id][-SESSION_MEMORY_MAX_TURNS * 2:]


def get_history(session_id: str) -> list[dict]:
    """Returns the full message history for a session."""
    return _sessions.get(session_id, [])


def get_messages_for_llm(session_id: str) -> list[dict]:
    """Returns history formatted for LLM API (role + content only)."""
    return [
        {"role": m["role"], "content": m["content"]}
        for m in _sessions.get(session_id, [])
    ]


def clear_session(session_id: str) -> None:
    """Clears the session history."""
    if session_id in _sessions:
        del _sessions[session_id]


def list_sessions() -> list[str]:
    """Returns all active session IDs."""
    return list(_sessions.keys())
