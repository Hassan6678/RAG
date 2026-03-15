from __future__ import annotations

import os
from pathlib import Path
from typing import List, Sequence

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings

from .utils import compute_files_signature, ensure_dir


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

OLLAMA_MODELS = ["llama3.2:3b", "llama3.1:8b", "mistral:7b"]
EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_MODEL = "llama3.2:3b"

# When running in Docker, set OLLAMA_BASE_URL=http://ollama:11434 via env.
# Defaults to localhost for local development.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


# ---------------------------------------------------------------------------
# RAG Pipeline
# ---------------------------------------------------------------------------

class RAGPipeline:
    """End-to-end pipeline: PDF ingestion → FAISS indexing → conversational retrieval.

    Uses Ollama for both embeddings (nomic-embed-text) and chat (configurable).
    """

    def __init__(
        self,
        persist_base: Path,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.1,
        top_k: int = 4,
        chunk_size: int = 1200,
        chunk_overlap: int = 150,
    ) -> None:
        self.persist_base = ensure_dir(persist_base)
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_documents(self, pdf_paths: Sequence[Path]) -> List:
        """Load all PDFs and return a flat list of LangChain Document objects."""
        documents: List = []
        for pdf_path in pdf_paths:
            loader = PyPDFLoader(str(pdf_path))
            documents.extend(loader.load())
        return documents

    def prepare_index(self, pdf_paths: Sequence[Path]) -> Path:
        """Build (or reuse a cached) FAISS index for the given PDFs."""
        if not pdf_paths:
            raise ValueError("No PDF files were provided for indexing.")

        index_path = self._index_path_for(pdf_paths)
        if self._index_exists(index_path):
            return index_path

        documents = self.load_documents(pdf_paths)
        if not documents:
            raise ValueError(
                "Could not extract any content from the provided PDFs. "
                "Make sure the files contain selectable text (not scanned images)."
            )

        chunks = self._split_documents(documents)
        if not chunks:
            raise ValueError(
                "No extractable text found after splitting the PDFs. "
                "Please upload text-based PDFs or run OCR before uploading."
            )

        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(str(index_path))
        return index_path

    def get_chain(self, index_path: Path) -> ConversationalRetrievalChain:
        """Load the FAISS index and return a ready-to-use ConversationalRetrievalChain."""
        if not self._index_exists(index_path):
            raise FileNotFoundError(
                f"Vector index not found at '{index_path}'. "
                "Please process your documents first."
            )

        vectorstore = FAISS.load_local(
            str(index_path),
            OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL),
            allow_dangerous_deserialization=True,
        )

        llm = ChatOllama(model=self.model, temperature=self.temperature, base_url=OLLAMA_BASE_URL)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": self.top_k})

        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _index_path_for(self, pdf_paths: Sequence[Path]) -> Path:
        index_id = compute_files_signature(pdf_paths)
        return self.persist_base / index_id

    @staticmethod
    def _index_exists(index_path: Path) -> bool:
        return (
            (index_path / "index.faiss").exists()
            and (index_path / "index.pkl").exists()
        )

    def _split_documents(self, documents: List) -> List:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        chunks = splitter.split_documents(documents)
        return [doc for doc in chunks if (doc.page_content or "").strip()]
