"""
Configuration Management for AI Teacher.
Loads configuration from secrets.toml, .env, and environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Helper function to get config value from environment variables or default
def get_config(key: str, default: Optional[str] = None) -> str:
    val = os.getenv(key)
    if val is not None:
        return val
    return default or ""


# Core Settings
GROQ_API_KEY = get_config("GROQ_API_KEY")
GROQ_LLM_MODEL = get_config("GROQ_LLM_MODEL", "groq/compound")
GROQ_FALLBACK_LLM_MODEL = get_config("GROQ_FALLBACK_LLM_MODEL", "qwen/qwen3.8-27b")
GROQ_STT_MODEL = get_config("GROQ_STT_MODEL", "whisper-large-v3")

LANGSMITH_API_KEY = get_config("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = get_config("LANGSMITH_PROJECT", "ai-teacher-hackathon")

POLLINATIONS_API_KEY = get_config("POLLINATIONS_API_KEY")

DATABASE_URL = get_config("DATABASE_URL", f"sqlite:///{BASE_DIR / 'ai_teacher.db'}")
CHROMA_DB_DIR = str(BASE_DIR / "chroma_db")
MEDIA_CACHE_DIR = str(BASE_DIR / "media_cache")
UPLOADS_DIR = str(BASE_DIR / "uploads")

# Ensure required directories exist
for folder in [CHROMA_DB_DIR, MEDIA_CACHE_DIR, UPLOADS_DIR]:
    os.makedirs(folder, exist_ok=True)

# System capabilities detection
def is_groq_configured() -> bool:
    return bool(GROQ_API_KEY and len(GROQ_API_KEY.strip()) > 5)

def is_langsmith_configured() -> bool:
    return bool(LANGSMITH_API_KEY and len(LANGSMITH_API_KEY.strip()) > 5)
