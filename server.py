"""
API server entry point.

Usage:
    python server.py

    # or:
    uvicorn server:app --host 0.0.0.0 --port 8001 --reload
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.api.routes import app
from config import API_HOST, API_PORT

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
