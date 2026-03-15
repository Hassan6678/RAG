"""Welcome page — shown when no documents have been processed yet."""

from __future__ import annotations

import streamlit as st

from .constants import APP_ICON, APP_TITLE


class WelcomePage:
    """Simple centered prompt to get the user started."""

    def render(self) -> None:
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown(
                f'<div class="welcome-outer">'
                f'  <div class="welcome-icon-ring">{APP_ICON}</div>'
                f'  <h2 class="welcome-title">Welcome to {APP_TITLE}</h2>'
                f'  <p class="welcome-sub">'
                f'    Upload PDF documents in the sidebar and click<br>'
                f'    <strong>Process Documents</strong> to build your knowledge base.'
                f'  </p>'
                f'</div>',
                unsafe_allow_html=True,
            )
