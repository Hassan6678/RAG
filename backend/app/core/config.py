"""Application configuration — loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

# Ollama
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODELS: list[str] = ["llama3.2:3b", "llama3.1:8b", "mistral:7b"]
EMBEDDING_MODEL: str = "nomic-embed-text"
DEFAULT_MODEL: str = "llama3.2:3b"

# Paths
BASE_DIR: Path = Path(__file__).resolve().parents[2]  # backend/
CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", str(BASE_DIR / ".cache")))
UPLOAD_DIR: Path = CACHE_DIR / "uploads"
INDEX_DIR: Path = CACHE_DIR / "indexes"

# CORS
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
