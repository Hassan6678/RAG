"""Slim StreamlitUI orchestrator — wires all UI modules together."""

from __future__ import annotations

from typing import List, Tuple

import streamlit as st

from ..logic import RAGPipeline
from ..utils import get_cache_dir, load_env, save_uploaded_files
from .constants import APP_ICON, APP_TITLE
from .scripts import JS
from .sidebar import Sidebar
from .styles import CSS
from .welcome import WelcomePage
from .workspace import Workspace


class StreamlitUI:
    """Entry point: call `StreamlitUI().run()` from run.py."""

    def __init__(self) -> None:
        self._cache_dir  = get_cache_dir()
        self._upload_dir = self._cache_dir / "uploads"
        self._index_dir  = self._cache_dir / "indexes"

        self._sidebar   = Sidebar(on_process=self._initialize_chain)
        self._welcome   = WelcomePage()
        self._workspace = Workspace(on_question=self._run_chain)

    # ── Entry point ───────────────────────────────────────────────────────────
    def run(self) -> None:
        load_env()
        st.set_page_config(
            page_title=APP_TITLE,
            page_icon=APP_ICON,
            layout="wide",
            initial_sidebar_state="expanded",
        )
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown(JS,  unsafe_allow_html=True)

        self._init_session_state()

        pending = st.session_state.get("pending_prompt")
        st.session_state.pending_prompt = None

        self._sidebar.render()

        if st.session_state.chain is None:
            self._welcome.render()
        else:
            self._workspace.render(pending)

    # ── Session state ─────────────────────────────────────────────────────────
    def _init_session_state(self) -> None:
        defaults: dict = {
            "messages":       [],
            "chain":          None,
            "docs_ready":     False,
            "doc_names":      [],
            "active_model":   None,
            "last_sources":   [],
            "pending_prompt": None,
        }
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

    # ── Chain operations ──────────────────────────────────────────────────────
    def _initialize_chain(self, model: str, temperature: float, uploaded_files: List) -> None:
        if not uploaded_files:
            st.error("Please upload at least one PDF document.")
            return

        progress = st.progress(0, text="Saving uploaded files…")
        try:
            saved_paths = save_uploaded_files(uploaded_files, self._upload_dir)
            progress.progress(25, text="Building vector index…")

            pipeline   = RAGPipeline(
                persist_base=self._index_dir,
                model=model,
                temperature=temperature,
            )
            index_path = pipeline.prepare_index(saved_paths)
            progress.progress(75, text="Wiring retrieval chain…")

            st.session_state.chain        = pipeline.get_chain(index_path)
            st.session_state.messages     = []
            st.session_state.docs_ready   = True
            st.session_state.doc_names    = [f.name for f in uploaded_files]
            st.session_state.active_model = model
            st.session_state.last_sources = []

            progress.progress(100, text="Done!")
            st.success(f"✅ {len(uploaded_files)} document(s) indexed with **{model}**.")
            st.rerun()

        except Exception as exc:
            progress.empty()
            st.error("**Failed to build the knowledge base.**")
            with st.expander("Error details"):
                st.exception(exc)

    def _run_chain(self, question: str) -> Tuple[str, list]:
        try:
            response = st.session_state.chain.invoke({"question": question})
            answer   = response.get("answer", "") if isinstance(response, dict) else str(response)
            sources  = response.get("source_documents", []) if isinstance(response, dict) else []
        except Exception as exc:
            answer, sources = f"**An error occurred:** {exc}", []
        return answer, sources
