"""FastAPI routes — upload, index, chat, sources, health."""

from __future__ import annotations

import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..core.config import OLLAMA_BASE_URL, OLLAMA_MODELS, DEFAULT_MODEL
from ..schemas.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    IndexRequest,
    IndexResponse,
    ModelsResponse,
    SessionInfo,
    SessionRequest,
    SourceItem,
    UploadResponse,
)
from ..services import rag_service

router = APIRouter()

# Thread pool for CPU/IO-bound LangChain + FAISS + Ollama operations.
# These are synchronous and would freeze the async event loop without this.
_executor = ThreadPoolExecutor(max_workers=2)


async def _run_sync(fn, *args, **kwargs):
    """Run a synchronous function in the thread pool without blocking the event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _executor, functools.partial(fn, *args, **kwargs)
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", ollama_url=OLLAMA_BASE_URL)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

@router.get("/api/models", response_model=ModelsResponse)
async def list_models():
    return ModelsResponse(models=OLLAMA_MODELS, default=DEFAULT_MODEL)


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

@router.post("/api/upload", response_model=UploadResponse)
async def upload(
    session_id: str = Form(...),
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(400, "No files provided.")

    pairs: list[tuple[str, bytes]] = []
    for f in files:
        if not f.filename or not f.filename.lower().endswith(".pdf"):
            raise HTTPException(400, f"Only PDF files allowed. Got: {f.filename}")
        data = await f.read()
        if len(data) == 0:
            raise HTTPException(400, f"File '{f.filename}' is empty.")
        pairs.append((f.filename, data))

    try:
        names = await _run_sync(rag_service.upload_files, session_id, pairs)
    except Exception as e:
        raise HTTPException(500, str(e))

    return UploadResponse(
        uploaded=names,
        message=f"{len(names)} file(s) uploaded successfully.",
    )


# ---------------------------------------------------------------------------
# Index  (heavy — embedding all chunks via Ollama, runs in thread pool)
# ---------------------------------------------------------------------------

@router.post("/api/index", response_model=IndexResponse)
async def index_docs(req: IndexRequest):
    try:
        result = await _run_sync(
            rag_service.index_documents,
            session_id=req.session_id,
            model=req.model,
            temperature=req.temperature,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

    return IndexResponse(
        indexed=result["indexed"],
        model=result["model"],
        message=f'{result["indexed"]} document(s) indexed with {result["model"]}.',
    )


# ---------------------------------------------------------------------------
# Chat  (heavy — LLM inference via Ollama, runs in thread pool)
# ---------------------------------------------------------------------------

@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        result = await _run_sync(rag_service.chat, req.session_id, req.question)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

    return ChatResponse(
        answer=result["answer"],
        sources=[SourceItem(**s) for s in result["sources"]],
    )


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

@router.get("/api/sources")
async def get_sources(session_id: str):
    sources = rag_service.get_sources(session_id)
    return {"sources": sources}


# ---------------------------------------------------------------------------
# Session info
# ---------------------------------------------------------------------------

@router.get("/api/session", response_model=SessionInfo)
async def session_info(session_id: str):
    return rag_service.get_session_info(session_id)


# ---------------------------------------------------------------------------
# Clear / New chat
# ---------------------------------------------------------------------------

@router.post("/api/clear")
async def clear(req: SessionRequest):
    rag_service.clear_session(req.session_id)
    return {"message": "Session cleared."}
