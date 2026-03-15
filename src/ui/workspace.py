"""Workspace UI — chat column + sources panel, shown after docs are loaded."""

from __future__ import annotations

import os
from typing import Callable, Optional, Tuple

import streamlit as st

from .constants import APP_ICON, APP_TITLE, PROMPT_CHIPS

# Position-based relevance scores (first hit = most relevant)
_RELEVANCE = [94, 87, 81, 75, 70]

# Inline SVG robot illustration (blue/purple tones matching the design)
_ROBOT_SVG = """
<svg viewBox="0 0 220 200" xmlns="http://www.w3.org/2000/svg" style="width:160px;height:auto;">
  <!-- Shadow -->
  <ellipse cx="110" cy="192" rx="55" ry="6" fill="#D6DEFF" opacity="0.5"/>
  <!-- Body -->
  <rect x="60" y="72" width="100" height="80" rx="20" fill="#E8EDFF" stroke="#B8C4FF" stroke-width="2"/>
  <!-- Screen / chest -->
  <rect x="76" y="88" width="68" height="40" rx="10" fill="#FFFFFF" stroke="#C5D0FF" stroke-width="1.5"/>
  <circle cx="96"  cy="108" r="5" fill="#4F7BFF" opacity="0.6"/>
  <circle cx="110" cy="108" r="5" fill="#7C3AED" opacity="0.5"/>
  <circle cx="124" cy="108" r="5" fill="#4F7BFF" opacity="0.6"/>
  <!-- Head -->
  <rect x="68" y="18" width="84" height="58" rx="18" fill="#D6DEFF" stroke="#A8B8FF" stroke-width="2"/>
  <!-- Eyes -->
  <ellipse cx="92"  cy="44" rx="10" ry="11" fill="#FFFFFF" stroke="#A8B8FF" stroke-width="1.5"/>
  <ellipse cx="128" cy="44" rx="10" ry="11" fill="#FFFFFF" stroke="#A8B8FF" stroke-width="1.5"/>
  <circle cx="94"  cy="43" r="5" fill="#4F7BFF"/>
  <circle cx="130" cy="43" r="5" fill="#4F7BFF"/>
  <circle cx="96"  cy="41" r="2" fill="#FFFFFF"/>
  <circle cx="132" cy="41" r="2" fill="#FFFFFF"/>
  <!-- Smile -->
  <path d="M96 56 Q110 66 124 56" fill="none" stroke="#4F7BFF" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Antenna -->
  <line x1="110" y1="18" x2="110" y2="6" stroke="#A8B8FF" stroke-width="3" stroke-linecap="round"/>
  <circle cx="110" cy="4" r="5" fill="#4F7BFF"/>
  <!-- Arms -->
  <rect x="34" y="86" width="28" height="14" rx="7" fill="#D6DEFF" stroke="#A8B8FF" stroke-width="1.5"/>
  <rect x="158" y="86" width="28" height="14" rx="7" fill="#D6DEFF" stroke="#A8B8FF" stroke-width="1.5"/>
  <!-- Hands -->
  <circle cx="34"  cy="93" r="7" fill="#C5D0FF" stroke="#A8B8FF" stroke-width="1.5"/>
  <circle cx="186" cy="93" r="7" fill="#C5D0FF" stroke="#A8B8FF" stroke-width="1.5"/>
  <!-- Legs -->
  <rect x="80"  y="152" width="18" height="24" rx="8" fill="#D6DEFF" stroke="#A8B8FF" stroke-width="1.5"/>
  <rect x="122" y="152" width="18" height="24" rx="8" fill="#D6DEFF" stroke="#A8B8FF" stroke-width="1.5"/>
  <!-- Feet -->
  <rect x="74"  y="170" width="30" height="14" rx="7" fill="#C5D0FF" stroke="#A8B8FF" stroke-width="1.5"/>
  <rect x="116" y="170" width="30" height="14" rx="7" fill="#C5D0FF" stroke="#A8B8FF" stroke-width="1.5"/>
  <!-- Ear accents -->
  <rect x="56" y="32" width="12" height="20" rx="6" fill="#C5D0FF" stroke="#A8B8FF" stroke-width="1.5"/>
  <rect x="152" y="32" width="12" height="20" rx="6" fill="#C5D0FF" stroke="#A8B8FF" stroke-width="1.5"/>
</svg>
"""


class RightPanel:
    """Sources panel with relevance bars, thumbnails, and session info."""

    def render(self) -> None:
        st.markdown("<div class='rp-wrap'>", unsafe_allow_html=True)
        _docs, count = self._sources()
        if count:
            st.markdown(
                f'<div class="rp-retrieved">'
                f'  📨 Retrieved <strong>{count}</strong> source{"s" if count != 1 else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("<div class='rp-rule'></div>", unsafe_allow_html=True)
        self._session_stats()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Private ───────────────────────────────────────────────────────────────
    def _sources(self) -> Tuple[list, int]:
        st.markdown(
            "<div class='rp-top-bar'>"
            "  <span class='rp-title'>📑 Sources</span>"
            "  <span class='rp-more'>···</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        docs = st.session_state.get("last_sources", [])
        if not docs:
            st.markdown(
                '<div class="rp-empty">'
                '  <div class="rp-empty-icon">📄</div>'
                '  <div class="rp-empty-text">Sources appear here<br>after your first question</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            return [], 0

        seen: set = set()
        rendered = 0
        for doc in docs[:5]:
            raw    = doc.metadata.get("source", "Unknown")
            name   = os.path.basename(raw)
            page   = doc.metadata.get("page")
            pg_lbl = f"Page {page + 1}" if isinstance(page, int) else ""
            key    = f"{name}_{pg_lbl}"
            if key in seen:
                continue
            seen.add(key)

            pct     = _RELEVANCE[min(rendered, len(_RELEVANCE) - 1)]
            excerpt = (doc.page_content or "")[:160].replace("\n", " ").strip()
            page_html = f'<div class="src-page">{pg_lbl}</div>' if pg_lbl else ""

            st.markdown(
                f'<div class="src-card">'
                f'  <div class="src-filename">{name}</div>'
                f'  {page_html}'
                f'  <div class="src-rel-row">'
                f'    <div class="src-rel-track">'
                f'      <div class="src-rel-fill" style="width:{pct}%"></div>'
                f'    </div>'
                f'    <span class="src-rel-pct">{pct}%</span>'
                f'  </div>'
                f'  <div class="src-thumb">'
                f'    <div class="src-thumb-lines">'
                f'      <div class="src-thumb-line" style="width:100%"></div>'
                f'      <div class="src-thumb-line" style="width:80%"></div>'
                f'      <div class="src-thumb-line" style="width:92%"></div>'
                f'      <div class="src-thumb-line" style="width:68%"></div>'
                f'    </div>'
                f'  </div>'
                f'  <div class="src-excerpt">{excerpt}…</div>'
                f'  <span class="src-expand">Expand</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            rendered += 1

        return docs, rendered

    def _session_stats(self) -> None:
        st.markdown(
            "<div class='rp-heading'>⚙️ Session</div>",
            unsafe_allow_html=True,
        )
        model = st.session_state.active_model or "—"
        temp  = st.session_state.get("sb_temp", 0.1)
        ndocs = len(st.session_state.doc_names)
        rows = "".join(
            f'<div class="stat-row">'
            f'  <span class="stat-key">{k}</span>'
            f'  <span class="stat-val">{v}</span>'
            f'</div>'
            for k, v in [("Model", model), ("Temp", f"{temp:.2f}"), ("Docs", str(ndocs))]
        )
        st.markdown(f'<div class="stat-block">{rows}</div>', unsafe_allow_html=True)


class Workspace:
    """2-column workspace: chat on the left, sources panel on the right.

    Args:
        on_question: Called with (question: str) -> (answer: str, sources: list).
    """

    def __init__(self, on_question: Callable[[str], Tuple[str, list]]) -> None:
        self._on_question = on_question
        self._panel       = RightPanel()

    # ── Public ────────────────────────────────────────────────────────────────
    def render(self, pending: Optional[str] = None) -> None:
        col_chat, col_panel = st.columns([7, 3], gap="large")

        with col_chat:
            self._ws_bar()
            self._messages()

        with col_panel:
            self._panel.render()

        self._chat_input(pending)

    # ── Private ───────────────────────────────────────────────────────────────
    def _ws_bar(self) -> None:
        model_name = st.session_state.active_model or ""
        doc_count  = len(st.session_state.doc_names)
        st.markdown(
            f'<div class="ws-bar">'
            f'  <div class="ws-bar-left">'
            f'    <span class="ws-bar-icon">{APP_ICON}</span>'
            f'    <span class="ws-bar-title">{APP_TITLE}</span>'
            f'  </div>'
            f'  <div class="ws-bar-right">'
            f'    <span class="ws-chip">{model_name}</span>'
            f'    <span class="ws-chip">📚 {doc_count} doc{"s" if doc_count != 1 else ""}</span>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    def _messages(self) -> None:
        if not st.session_state.messages:
            self._empty_state()
            return

        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else APP_ICON
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    def _empty_state(self) -> None:
        """Robot illustration + suggestion chips — no nested columns."""
        st.markdown(
            f'<div class="ws-empty">'
            f'  <div class="ws-robot">{_ROBOT_SVG}</div>'
            f'  <h2 class="ws-empty-title">Ask questions about your documents 📄</h2>'
            f'  <p class="ws-empty-sub">Ask anything about the documents you\'ve uploaded</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Chips rendered as sequential buttons (avoids nested st.columns)
        for chip in PROMPT_CHIPS[:3]:
            if st.button(f"{chip}  ›", key=f"chip_{chip}", use_container_width=True):
                st.session_state.pending_prompt = chip
                st.rerun()

    def _chat_input(self, pending: Optional[str]) -> None:
        user_input = st.chat_input("Type a message…")
        question   = pending or user_input

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("Thinking…"):
                answer, sources = self._on_question(question)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.last_sources = sources
            st.rerun()
