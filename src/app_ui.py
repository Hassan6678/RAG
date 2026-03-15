from __future__ import annotations

import os
from typing import List, Tuple

import streamlit as st

from .logic import OLLAMA_MODELS, RAGPipeline
from .utils import (
    get_cache_dir,
    load_env,
    save_uploaded_files,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_TITLE = "DocMind AI"
APP_SUBTITLE = "Ask questions across your documents — powered by RAG + local Ollama LLM"
APP_ICON = "🧠"

WELCOME_BULLETS = [
    "🖥️ Make sure **Ollama is installed and running** locally",
    "📦 Pull the required models: `ollama pull llama3.2:3b` and `ollama pull nomic-embed-text`",
    "📄 Upload one or more **PDF documents** in the sidebar",
    "💬 Click **Process Documents** and start asking questions",
]


class StreamlitUI:
    """Streamlit user interface for the local RAG chatbot."""

    def __init__(self) -> None:
        self.cache_dir = get_cache_dir()
        self.upload_dir = self.cache_dir / "uploads"
        self.index_dir = self.cache_dir / "indexes"

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def run(self) -> None:
        load_env()
        st.set_page_config(
            page_title=APP_TITLE,
            page_icon=APP_ICON,
            layout="wide",
            initial_sidebar_state="expanded",
        )
        self._inject_css()
        self._init_session_state()

        model, temperature, uploaded_files, process_clicked, clear_clicked = self._render_sidebar()

        if clear_clicked:
            self._clear_chat()

        if process_clicked:
            self._initialize_chain(model, temperature, uploaded_files)

        self._render_main()

    # ------------------------------------------------------------------
    # Session state
    # ------------------------------------------------------------------
    def _init_session_state(self) -> None:
        defaults: dict = {
            "messages": [],
            "chain": None,
            "docs_ready": False,
            "doc_names": [],
            "active_model": None,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------
    def _render_sidebar(self) -> Tuple:
        with st.sidebar:
            # Brand
            st.markdown(
                f"<div class='sidebar-brand'>{APP_ICON} {APP_TITLE}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<hr class='sidebar-hr'>", unsafe_allow_html=True)

            # ── Local setup note ────────────────────────────────────────
            st.markdown(
                "<div class='embed-note'>"
                "🖥️ <b>Local setup required</b><br>"
                "Make sure <b>Ollama</b> is installed and running.<br>"
                "Pull models before use:<br>"
                "<code>ollama pull llama3.2:3b</code><br>"
                "<code>ollama pull nomic-embed-text</code>"
                "</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<hr class='sidebar-hr'>", unsafe_allow_html=True)

            # ── Model selection ──────────────────────────────────────────
            st.markdown("**🤖 Model**")
            model = st.selectbox(
                "Chat model",
                options=OLLAMA_MODELS,
                index=0,
                label_visibility="collapsed",
                help="Ollama model to use for chat. Default: llama3.2:3b",
            )

            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.05,
                help="Lower = more factual. Higher = more creative.",
            )

            st.markdown("<hr class='sidebar-hr'>", unsafe_allow_html=True)

            # ── Document upload ────────────────────────────────────────
            st.markdown("**📂 Knowledge Base**")
            uploaded_files = st.file_uploader(
                "Upload PDF documents",
                type=["pdf"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )

            if uploaded_files:
                st.markdown(
                    f"<div class='file-count-badge'>📄 {len(uploaded_files)} file(s) selected</div>",
                    unsafe_allow_html=True,
                )
                with st.expander("View files", expanded=False):
                    for f in uploaded_files:
                        size_kb = round(len(f.getbuffer()) / 1024, 1)
                        st.caption(f"• {f.name} ({size_kb} KB)")

            process_clicked = st.button(
                "⚡ Process Documents",
                type="primary",
                disabled=not bool(uploaded_files),
                use_container_width=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Knowledge base status badge
            if st.session_state.docs_ready:
                active_model = st.session_state.active_model or ""
                st.markdown(
                    "<div class='status-badge status-ok'>✅ Knowledge base ready</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"Model: {active_model}")
                if st.session_state.doc_names:
                    with st.expander("Indexed documents", expanded=False):
                        for name in st.session_state.doc_names:
                            st.caption(f"• {name}")

            st.markdown("<hr class='sidebar-hr'>", unsafe_allow_html=True)

            clear_clicked = st.button(
                "🗑️ Clear Chat",
                use_container_width=True,
                disabled=not bool(st.session_state.messages),
            )

            st.markdown(
                "<div class='sidebar-footer'>Ollama · LangChain · FAISS · Streamlit</div>",
                unsafe_allow_html=True,
            )

        return (model, temperature, uploaded_files, process_clicked, clear_clicked)

    # ------------------------------------------------------------------
    # Document processing
    # ------------------------------------------------------------------
    def _initialize_chain(
        self,
        model: str,
        temperature: float,
        uploaded_files: List,
    ) -> None:
        if not uploaded_files:
            st.error("Please upload at least one PDF document.")
            return

        progress = st.progress(0, text="Saving uploaded files…")
        try:
            saved_paths = save_uploaded_files(uploaded_files, self.upload_dir)
            progress.progress(25, text="Building vector index (local embeddings)…")

            pipeline = RAGPipeline(
                persist_base=self.index_dir,
                model=model,
                temperature=temperature,
            )
            index_path = pipeline.prepare_index(saved_paths)
            progress.progress(75, text="Wiring local retrieval chain…")

            st.session_state.chain = pipeline.get_chain(index_path)
            st.session_state.messages = []
            st.session_state.docs_ready = True
            st.session_state.doc_names = [f.name for f in uploaded_files]
            st.session_state.active_model = model

            progress.progress(100, text="Done!")
            st.success(
                f"✅ Knowledge base ready — {len(uploaded_files)} document(s) indexed "
                f"using **{model}**. Start chatting!"
            )

        except Exception as exc:
            progress.empty()
            st.error("**Failed to build the knowledge base.** See details below.")
            with st.expander("Error details"):
                st.exception(exc)

    # ------------------------------------------------------------------
    # Main area
    # ------------------------------------------------------------------
    def _render_main(self) -> None:
        st.markdown(
            f"<h1 class='app-title'>{APP_ICON} {APP_TITLE}</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p class='app-subtitle'>{APP_SUBTITLE}</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr class='title-hr'>", unsafe_allow_html=True)

        if st.session_state.chain is None:
            self._render_welcome()
        else:
            self._render_chat()

    def _render_welcome(self) -> None:
        st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
        st.markdown("### Get started in 4 steps")
        for bullet in WELCOME_BULLETS:
            st.markdown(bullet)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Model showcase cards
        col1, col2, col3 = st.columns(3)
        cards = [
            ("🟢", "llama3.2:3b", "Default · Fast", "Lightweight, runs on most machines. Great for quick Q&A."),
            ("🔵", "llama3.1:8b", "Balanced · Accurate", "Better reasoning, needs ~6 GB VRAM or 8 GB RAM."),
            ("🟣", "mistral:7b", "Alternative", "Strong open-source model, good for structured documents."),
        ]
        for col, (dot, name, tag, desc) in zip([col1, col2, col3], cards):
            with col:
                st.markdown(
                    f"<div class='feature-card'>"
                    f"<div class='feature-icon'>{dot}</div>"
                    f"<div class='feature-title'>{name}</div>"
                    f"<div class='feature-models'>{tag}</div>"
                    f"<div class='feature-desc'>{desc}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        feat_col1, feat_col2, feat_col3 = st.columns(3)
        features = [
            ("🔍", "Semantic Search", "FAISS vector store for millisecond retrieval over thousands of pages."),
            ("🧠", "RAG Pipeline", "LangChain ConversationalRetrievalChain with full multi-turn memory."),
            ("📑", "Source Tracing", "Every answer cites the exact document and page number."),
        ]
        for col, (icon, title, desc) in zip([feat_col1, feat_col2, feat_col3], features):
            with col:
                st.markdown(
                    f"<div class='feature-card'>"
                    f"<div class='feature-icon'>{icon}</div>"
                    f"<div class='feature-title'>{title}</div>"
                    f"<div class='feature-desc'>{desc}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------
    def _render_chat(self) -> None:
        for message in st.session_state.messages:
            avatar = "🧠" if message["role"] == "assistant" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
                if message.get("sources"):
                    self._render_sources(message["sources"])

        user_input = st.chat_input("Ask a question about your documents…")
        if not user_input:
            return

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("Thinking…"):
                answer, sources = self._run_chain(user_input)
            st.markdown(answer)
            if sources:
                self._render_sources(sources)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )

    def _run_chain(self, question: str):
        try:
            response = st.session_state.chain.invoke({"question": question})
            answer = (
                response.get("answer", "") if isinstance(response, dict) else str(response)
            )
            sources = (
                response.get("source_documents", []) if isinstance(response, dict) else []
            )
        except Exception as exc:
            answer = f"**An error occurred:** {exc}"
            sources = []
        return answer, sources

    @staticmethod
    def _render_sources(sources: list) -> None:
        if not sources:
            return
        with st.expander(f"📑 {len(sources)} source(s) referenced"):
            seen: set = set()
            for doc in sources[:5]:
                raw_source = doc.metadata.get("source", "Unknown")
                source = os.path.basename(raw_source)
                page = doc.metadata.get("page")
                page_label = f", p. {page + 1}" if isinstance(page, int) else ""
                key = f"{source}{page_label}"
                if key not in seen:
                    seen.add(key)
                    st.markdown(f"- `{source}`{page_label}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clear_chat(self) -> None:
        st.session_state.messages = []
        if st.session_state.chain is not None:
            try:
                st.session_state.chain.memory.clear()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # CSS
    # ------------------------------------------------------------------
    def _inject_css(self) -> None:
        st.markdown(
            """
            <style>
            /* ── Global ── */
            #MainMenu, footer, header { visibility: hidden; }
            .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 880px; }

            /* ── App header ── */
            .app-title {
                font-size: 2rem; font-weight: 700;
                letter-spacing: -0.5px; margin-bottom: 0.15rem;
            }
            .app-subtitle { color: #9ca3af; font-size: 0.95rem; margin-top: 0; }
            .title-hr { border: none; border-top: 1px solid #2d2d2d; margin: 0.75rem 0 1.25rem; }

            /* ── Sidebar ── */
            [data-testid="stSidebar"] {
                background-color: #0f1117;
                border-right: 1px solid #1f2937;
            }
            .sidebar-brand { font-size: 1.25rem; font-weight: 700; color: #e5e7eb; padding: 0.25rem 0; }
            .sidebar-hr { border: none; border-top: 1px solid #1f2937; margin: 0.6rem 0; }
            .sidebar-footer { font-size: 0.72rem; color: #4b5563; text-align: center; padding-top: 0.5rem; }
            .embed-note {
                font-size: 0.78rem; color: #9ca3af;
                background: #1a2035; border: 1px solid #2d3748;
                border-radius: 6px; padding: 0.4rem 0.6rem; margin: 0.4rem 0;
            }

            /* ── Status badges ── */
            .status-badge {
                display: inline-block; padding: 0.3rem 0.65rem;
                border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-bottom: 0.25rem;
            }
            .status-ok  { background: #052e16; color: #4ade80; border: 1px solid #166534; }
            .status-warn{ background: #2d1a00; color: #fbbf24; border: 1px solid #78350f; }
            .file-count-badge {
                display: inline-block; padding: 0.25rem 0.6rem; border-radius: 6px;
                font-size: 0.78rem; background: #1e3a5f; color: #93c5fd;
                border: 1px solid #1d4ed8; margin-top: 0.4rem;
            }

            /* ── Feature / provider cards ── */
            .welcome-container {
                background: #111827; border: 1px solid #1f2937;
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
            }
            .feature-card {
                background: #111827; border: 1px solid #1f2937;
                border-radius: 10px; padding: 1.25rem 1rem; text-align: center;
            }
            .feature-icon   { font-size: 1.8rem; margin-bottom: 0.5rem; }
            .feature-title  { font-weight: 600; font-size: 0.95rem; color: #e5e7eb; margin-bottom: 0.25rem; }
            .feature-models { font-size: 0.75rem; color: #6b7280; margin-bottom: 0.4rem; font-style: italic; }
            .feature-desc   { font-size: 0.82rem; color: #6b7280; line-height: 1.4; }

            /* ── Chat ── */
            .stChatMessage { border-radius: 10px; padding: 0.6rem 0.75rem; margin-bottom: 0.4rem; }
            .stChatInput > div {
                border-radius: 10px; border-color: #374151 !important; background: #111827 !important;
            }

            /* ── Progress ── */
            .stProgress > div > div > div { background-color: #3b82f6; }

            /* ── Buttons ── */
            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #2563eb, #4f46e5);
                border: none; border-radius: 8px; font-weight: 600;
            }
            .stButton > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #1d4ed8, #4338ca);
                transform: translateY(-1px);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
