"""
config.py — Shared configuration and Groq client for both pipelines
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load .env from project root
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

# ── API Keys ──────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# ── Model settings ────────────────────────────────────────────
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ── Paths ─────────────────────────────────────────────────────
CORPUS_DIR = ROOT / "data" / "corpus"
CHROMA_DIR = ROOT / "data" / "chroma_db"
GRAPH_CACHE = ROOT / "data" / "graph_cache.json"
EVAL_DIR = ROOT / "evaluation"

# ── RAG settings ──────────────────────────────────────────────
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 5
MAX_TOKENS_GENERATION = 600
TEMPERATURE = 0.1          # Low temperature for factual banking queries

# ── Groq client singleton ─────────────────────────────────────
_groq_client = None

def get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not set. Add it to your .env file.\n"
                "Get a free key at: https://console.groq.com"
            )
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def generate(system_prompt: str, user_query: str, max_tokens: int = MAX_TOKENS_GENERATION) -> str:
    """Shared generation function — used by both pipelines."""
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        max_tokens=max_tokens,
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


def check_config() -> dict:
    """Check all configuration is valid. Returns status dict."""
    status = {
        "groq_key": bool(GROQ_API_KEY and len(GROQ_API_KEY) > 10),
        "neo4j_password": NEO4J_PASSWORD not in ("your_neo4j_password_here", "password", ""),
        "corpus_files": len(list(CORPUS_DIR.rglob("*.pdf"))) + len(list(CORPUS_DIR.rglob("*.txt"))),
        "chroma_exists": CHROMA_DIR.exists(),
        "graph_cache_exists": GRAPH_CACHE.exists(),
    }
    return status
