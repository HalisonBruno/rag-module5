"""
Reasoning engine.
- Decomposes complex questions into sub-questions
- Decides which source to consult (RAG docs, memory, or both)
"""
import json
from openai import OpenAI
from anthropic import Anthropic
from config import (
    DEFAULT_PROVIDER, OPENAI_API_KEY, ANTHROPIC_API_KEY,
    OPENAI_CHAT_MODEL, ANTHROPIC_CHAT_MODEL
)

_openai = OpenAI(api_key=OPENAI_API_KEY)
_anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)


def _call_llm(prompt: str, system: str) -> str:
    """Calls the default LLM and returns the text response."""
    if DEFAULT_PROVIDER == "openai":
        response = _openai.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt}
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    else:
        response = _anthropic.messages.create(
            model=ANTHROPIC_CHAT_MODEL,
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()


def decide_source(question: str, has_memory: bool) -> dict:
    """
    Decides where to look for the answer.

    Returns:
        {
            "use_rag":    True/False,  # search document index
            "use_memory": True/False,  # use session/persistent memory
            "reasoning":  "..."        # explanation
        }
    """
    system = """You are a routing assistant. Decide where to look for the answer.
Reply ONLY with valid JSON, no markdown, no explanation outside the JSON.
Format: {"use_rag": true/false, "use_memory": true/false, "reasoning": "..."}

Rules:
- use_rag=true if the question likely requires information from documents
- use_memory=true if the question refers to previous conversation or user preferences
- Both can be true simultaneously"""

    prompt = f"""Question: {question}
Has session memory available: {has_memory}

Where should I look for the answer?"""

    try:
        raw = _call_llm(prompt, system)
        return json.loads(raw)
    except Exception:
        return {"use_rag": True, "use_memory": has_memory, "reasoning": "fallback"}


def decompose_question(question: str) -> list[str]:
    """
    Breaks a complex question into simpler sub-questions.
    Returns a list of sub-questions (or just the original if it's simple).
    """
    system = """You are a question decomposition assistant.
If the question is simple and self-contained, return it as-is in a JSON array.
If the question is complex or multi-part, break it into 2-4 simpler sub-questions.
Reply ONLY with a valid JSON array of strings. No markdown, no explanation.
Example: ["What is X?", "How does Y work?"]"""

    prompt = f"Decompose this question if needed: {question}"

    try:
        raw = _call_llm(prompt, system)
        result = json.loads(raw)
        if isinstance(result, list) and all(isinstance(q, str) for q in result):
            return result
        return [question]
    except Exception:
        return [question]


def extract_facts_to_remember(question: str, answer: str) -> list[str]:
    """
    Extracts important facts from a Q&A pair worth saving to persistent memory.
    Returns a list of facts (may be empty if nothing important).
    """
    system = """You are a memory extraction assistant.
Extract important facts, preferences, or context from this Q&A that would be useful to remember for future conversations.
If nothing important, return an empty array.
Reply ONLY with a valid JSON array of strings."""

    prompt = f"Q: {question}\nA: {answer}"

    try:
        raw = _call_llm(prompt, system)
        result = json.loads(raw)
        if isinstance(result, list):
            return [f for f in result if isinstance(f, str)]
        return []
    except Exception:
        return []
