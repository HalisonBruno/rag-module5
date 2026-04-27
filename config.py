import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "claude")
OPENAI_CHAT_MODEL = "gpt-4o-mini"
ANTHROPIC_CHAT_MODEL = "claude-sonnet-4-5"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# --- Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# --- Memory ---
SESSION_MEMORY_MAX_TURNS = int(os.getenv("SESSION_MEMORY_MAX_TURNS", "20"))
PERSISTENT_MEMORY_MAX_ITEMS = int(os.getenv("PERSISTENT_MEMORY_MAX_ITEMS", "50"))

# --- RAG ---
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_THRESHOLD = float(os.getenv("RAG_THRESHOLD", "0.3"))

# --- API ---
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
