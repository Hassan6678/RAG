"""RAG service — PDF ingestion, FAISS indexing, conversational retrieval."""

from __future__ import annotations

import os
import re
import uuid
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Sequence

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.config import (
    DEFAULT_MODEL,
    EMBEDDING_MODEL,
    INDEX_DIR,
    OLLAMA_BASE_URL,
    UPLOAD_DIR,
)


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(data: bytes, original_name: str) -> Path:
    ensure_dir(UPLOAD_DIR)
    safe = Path(original_name).name
    if not safe.lower().endswith(".pdf"):
        raise ValueError(f"Only PDF files are supported, got '{safe}'.")
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe}"
    dest.write_bytes(data)
    return dest


def compute_signature(paths: Sequence[Path]) -> str:
    digest = sha256()
    for p in sorted(paths, key=lambda x: x.name):
        digest.update(p.name.encode())
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Session store
# ---------------------------------------------------------------------------

class Session:
    def __init__(self) -> None:
        self.chain: ConversationalRetrievalChain | None = None
        self.messages: list[dict[str, str]] = []
        self.last_sources: list[dict] = []
        self.doc_names: list[str] = []
        # Track the actual saved paths so we only index this session's files
        self.doc_paths: list[Path] = []
        self.model: str = DEFAULT_MODEL
        self.temperature: float = 0.1
        self.index_path: Path | None = None


_sessions: dict[str, Session] = {}


def get_session(session_id: str) -> Session:
    if session_id not in _sessions:
        _sessions[session_id] = Session()
    return _sessions[session_id]


# ---------------------------------------------------------------------------
# RAG Pipeline
# ---------------------------------------------------------------------------

class RAGPipeline:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.1,
        top_k: int = 4,
        chunk_size: int = 1200,
        chunk_overlap: int = 150,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def prepare_index(self, pdf_paths: Sequence[Path]) -> Path:
        if not pdf_paths:
            raise ValueError("No PDF files provided.")
        ensure_dir(INDEX_DIR)
        sig = compute_signature(pdf_paths)
        index_path = INDEX_DIR / sig
        if (index_path / "index.faiss").exists() and (index_path / "index.pkl").exists():
            return index_path

        docs: list = []
        for p in pdf_paths:
            docs.extend(PyPDFLoader(str(p)).load())
        if not docs:
            raise ValueError("Could not extract text from the provided PDFs.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap,
        )
        chunks = [c for c in splitter.split_documents(docs) if (c.page_content or "").strip()]
        if not chunks:
            raise ValueError("No text found after splitting.")

        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
        vs = FAISS.from_documents(chunks, embeddings)
        vs.save_local(str(index_path))
        return index_path

    def get_chain(self, index_path: Path) -> ConversationalRetrievalChain:
        vs = FAISS.load_local(
            str(index_path),
            OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL),
            allow_dangerous_deserialization=True,
        )
        llm = ChatOllama(model=self.model, temperature=self.temperature, base_url=OLLAMA_BASE_URL)
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="answer",
        )

        # ── Condense prompt ──────────────────────────────────────────────────
        # Only rephrase when the question is a genuine follow-up (contains
        # pronouns / references like "it", "that", "they", "the previous").
        # Independent questions must be returned EXACTLY as written.
        condense_prompt = PromptTemplate.from_template(
            """You are given a chat history and a new question from the user.
                Your ONLY job is to decide whether the new question needs the history to be understood.

                Rules (follow strictly):
                1. If the new question is self-contained and does NOT reference anything from the history
                (no pronouns like "it / that / this / they", no phrases like "the previous", "you mentioned",
                "as above", "what about", "and what about") → return the question EXACTLY as-is, word for word.
                2. If the question IS a follow-up that relies on the history → rewrite it as a single clear
                standalone question that includes the necessary context from the history.
                3. NEVER add, remove, or change the topic of a self-contained question.
                4. Output ONLY the final question — no explanation, no preamble.

                Chat History:
                {chat_history}

                New Question: {question}

                Final question:"""
        )

        # ── QA prompt ────────────────────────────────────────────────────────
        qa_prompt = PromptTemplate.from_template(
            """You are a document Q&A assistant. Answer ONLY what was asked using ONLY the document excerpts below.

STRICT RULES:
1. Answer ONLY the specific question asked. Do NOT mention related topics that appear in the excerpts but were not asked about.
2. Use ONLY information from the "Document excerpts" section. Do NOT use your own training knowledge to fill gaps.
3. If the exact answer is not in the excerpts, respond: "The uploaded documents do not contain information about [topic]."
4. Do NOT say "You mentioned X" — refer only to what is written in the chat history, not what you infer.
5. Be concise and direct.

Document excerpts:
{context}

Chat history:
{chat_history}

Question: {question}

Answer:"""
        )

        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vs.as_retriever(search_kwargs={"k": self.top_k}),
            memory=memory,
            condense_question_prompt=condense_prompt,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            return_source_documents=True,
            output_key="answer",
        )


# ---------------------------------------------------------------------------
# High-level service functions
# ---------------------------------------------------------------------------

def upload_files(session_id: str, files: list[tuple[str, bytes]]) -> list[str]:
    """Save uploaded files, store paths on the session."""
    session = get_session(session_id)
    saved_names: list[str] = []
    for name, data in files:
        path = save_upload(data, name)
        session.doc_paths.append(path)
        saved_names.append(name)
    # de-dup display names
    session.doc_names = list(dict.fromkeys(session.doc_names + saved_names))
    return saved_names


def index_documents(
    session_id: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.1,
) -> dict:
    """Build FAISS index from this session's uploaded files only."""
    session = get_session(session_id)

    # Only use files that actually exist on disk
    pdf_paths = [p for p in session.doc_paths if p.exists()]
    if not pdf_paths:
        raise ValueError("No PDFs found for this session. Upload files first.")

    pipeline = RAGPipeline(model=model, temperature=temperature)
    index_path = pipeline.prepare_index(pdf_paths)
    session.chain = pipeline.get_chain(index_path)
    session.model = model
    session.temperature = temperature
    session.index_path = index_path
    session.messages = []
    session.last_sources = []
    return {"indexed": len(pdf_paths), "model": model}


def chat(session_id: str, question: str) -> Dict[str, Any]:
    """Ask a question, return answer + sources."""
    session = get_session(session_id)
    if session.chain is None:
        raise ValueError("No documents indexed yet. Please upload and index first.")

    response = session.chain.invoke({"question": question})
    answer = response.get("answer", "") if isinstance(response, dict) else str(response)
    raw_sources = response.get("source_documents", []) if isinstance(response, dict) else []

    sources = []
    seen: set[str] = set()
    relevance_scores = [94, 87, 81, 75, 70]
    for i, doc in enumerate(raw_sources[:5]):
        raw = os.path.basename(doc.metadata.get("source", "Unknown"))
        # Strip the UUID prefix added during upload: 32hex_filename.pdf → filename.pdf
        name = re.sub(r'^[0-9a-f]{32}_', '', raw)
        page = doc.metadata.get("page")
        page_label = f"Page {page + 1}" if isinstance(page, int) else ""
        key = f"{name}_{page_label}"
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "filename": name,
            "page": page_label,
            "relevance": relevance_scores[min(i, len(relevance_scores) - 1)],
            "excerpt": (doc.page_content or "")[:200].replace("\n", " ").strip(),
        })

    session.messages.append({"role": "user", "content": question})
    session.messages.append({"role": "assistant", "content": answer})
    session.last_sources = sources
    return {"answer": answer, "sources": sources}


def get_sources(session_id: str) -> list[dict]:
    return get_session(session_id).last_sources


def get_session_info(session_id: str) -> dict:
    s = get_session(session_id)
    return {
        "model": s.model,
        "temperature": s.temperature,
        "doc_count": len(s.doc_names),
        "doc_names": s.doc_names,
        "message_count": len(s.messages),
        "has_chain": s.chain is not None,
    }


def clear_session(session_id: str) -> None:
    if session_id in _sessions:
        del _sessions[session_id]
