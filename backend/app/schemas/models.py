"""Pydantic request/response schemas for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class IndexRequest(BaseModel):
    session_id: str = Field(..., description="Client session identifier")
    model: str = Field(default="llama3.2:3b", description="Ollama model name")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)


class ChatRequest(BaseModel):
    session_id: str
    question: str = Field(..., min_length=1, description="User question")


class SessionRequest(BaseModel):
    session_id: str


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
    ollama_url: str


class UploadResponse(BaseModel):
    uploaded: list[str]
    message: str


class IndexResponse(BaseModel):
    indexed: int
    model: str
    message: str


class SourceItem(BaseModel):
    filename: str
    page: str
    relevance: int
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class SessionInfo(BaseModel):
    model: str
    temperature: float
    doc_count: int
    doc_names: list[str]
    message_count: int
    has_chain: bool


class ModelsResponse(BaseModel):
    models: list[str]
    default: str


class ErrorResponse(BaseModel):
    detail: str
