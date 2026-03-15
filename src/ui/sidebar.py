"""Sidebar UI component — clean white design with file list and model settings."""

from __future__ import annotations

from typing import Callable, List

import streamlit as st

from ..logic import OLLAMA_MODELS
from .constants import APP_ICON, APP_TITLE

# Dot colors for different file types
_DOT_COLORS = {
    "pdf":  "#EF4444",
    "xlsx": "#10B981",
    "xls":  "#10B981",
    "csv":  "#3B82F6",
    "docx": "#8B5CF6",
    "txt":  "#F59E0B",
}


def _dot_color(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return _DOT_COLORS.get(ext, "#94A3B8")


class Sidebar:
    """Renders the full left sidebar.

    Args:
        on_process: Called with (model, temperature, uploaded_files) when
                    the user clicks 'Process Documents'.
    """

    def __init__(self, on_process: Callable[[str, float, List], None]) -> None:
        self._on_process = on_process

    # ── Public ────────────────────────────────────────────────────────────────
    def render(self) -> None:
        with st.sidebar:
            self._header()
            st.markdown("<div style='padding:0.75rem 1rem 0'>", unsafe_allow_html=True)
            self._new_chat_btn()
            st.markdown("</div>", unsafe_allow_html=True)
            self._documents_section()
            st.markdown("<div style='flex:1; min-height:1rem'></div>", unsafe_allow_html=True)
            self._model_section()
            self._footer()

    # ── Private sections ──────────────────────────────────────────────────────
    def _header(self) -> None:
        st.markdown(
            f'<div class="sb-header">'
            f'  <div class="sb-logo">'
            f'    <div class="sb-logo-icon">{APP_ICON}</div>'
            f'    <span class="sb-logo-name">{APP_TITLE}</span>'
            f'  </div>'
            f'  <div class="sb-header-acts">'
            f'    <span class="sb-act-btn">⚙</span>'
            f'    <span class="sb-act-btn">···</span>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    def _new_chat_btn(self) -> None:
        if st.button("＋  New Chat", key="btn_new_chat", use_container_width=True, type="primary"):
            st.session_state.update({
                "messages": [], "chain": None,
                "docs_ready": False, "last_sources": [],
                "active_model": None, "doc_names": [],
            })
            st.rerun()

    def _documents_section(self) -> None:
        st.markdown("<div class='sb-rule'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sb-section'>DOCUMENTS</div>", unsafe_allow_html=True)

        # File upload
        uploaded_files = st.file_uploader(
            "Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded_files:
            st.markdown(
                f"<div class='status-chip chip-blue'>"
                f"  📄 {len(uploaded_files)} file(s) selected"
                f"</div>",
                unsafe_allow_html=True,
            )

        if st.button(
            "⚡  Process Documents",
            type="primary",
            disabled=not bool(uploaded_files),
            use_container_width=True,
            key="btn_process",
        ):
            self._on_process(
                st.session_state.get("sb_model", OLLAMA_MODELS[0]),
                st.session_state.get("sb_temp", 0.1),
                uploaded_files,
            )

        # Indexed file list
        if st.session_state.docs_ready and st.session_state.doc_names:
            st.markdown(
                f"<div class='status-chip chip-green'>"
                f"  ✅ {len(st.session_state.doc_names)} indexed"
                f"</div>",
                unsafe_allow_html=True,
            )
            for name in st.session_state.doc_names:
                color = _dot_color(name)
                short = name if len(name) <= 26 else name[:24] + "…"
                st.markdown(
                    f'<div class="sb-file-item">'
                    f'  <div class="sb-file-dot" style="background:{color}"></div>'
                    f'  <span class="sb-file-name" title="{name}">{short}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Clear chat button
        if st.session_state.get("messages"):
            if st.button(
                "🗑️  Clear Chat",
                use_container_width=True,
                key="btn_clear",
            ):
                st.session_state.messages     = []
                st.session_state.last_sources = []
                if st.session_state.chain is not None:
                    try:
                        st.session_state.chain.memory.clear()
                    except Exception:
                        pass

    def _model_section(self) -> None:
        st.markdown("<div class='sb-rule'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sb-section'>MODEL &amp; SETTINGS</div>", unsafe_allow_html=True)

        st.selectbox(
            "Chat model",
            options=OLLAMA_MODELS,
            index=0,
            label_visibility="collapsed",
            key="sb_model",
        )

        temp_val = st.session_state.get("sb_temp", 0.1)
        st.markdown(
            f"<div class='temp-row'>"
            f"  <span class='temp-label'>Temperature</span>"
            f"  <span class='temp-val'>{temp_val:.2f}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=0.1, step=0.05,
            label_visibility="collapsed",
            help="Lower = factual · Higher = creative",
            key="sb_temp",
        )

    def _footer(self) -> None:
        st.markdown("<div class='sb-rule'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='sb-footer-item'>"
            "  <span class='sb-footer-icon'>🤖</span>"
            "  Ollama · LangChain · FAISS"
            "</div>",
            unsafe_allow_html=True,
        )
