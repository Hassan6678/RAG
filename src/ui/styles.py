"""
Design system — clean white/light-gray theme, Inter, #4F7BFF accent.

Sections: BASE · SIDEBAR · BUTTONS · WELCOME · WORKSPACE · RIGHT PANEL · OVERRIDES
"""

CSS = """
<style>

/* ══════════════════════════════════════════
   BASE
══════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    background-color: #F0F4F8 !important;
    color: #1A202C !important;
}

/* Force light on every Streamlit layout layer */
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
.main, .main > div {
    background-color: #F0F4F8 !important;
    color: #1A202C !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 1.25rem 1.75rem 5rem !important;
    max-width: 100% !important;
}


/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E9ECF2 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    display: flex;
    flex-direction: column;
}

/* ── Header ── */
.sb-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1rem 0.85rem;
    border-bottom: 1px solid #F3F4F6;
}
.sb-logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.sb-logo-icon {
    width: 30px; height: 30px;
    background: linear-gradient(135deg, #4F7BFF 0%, #7C3AED 100%);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
}
.sb-logo-name {
    font-size: 0.92rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.2px;
}
.sb-header-acts { display: flex; align-items: center; gap: 0.3rem; }
.sb-act-btn {
    width: 26px; height: 26px;
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.7rem; color: #9CA3AF;
    cursor: pointer;
}

/* ── Section labels ── */
.sb-section {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    color: #9CA3AF;
    text-transform: uppercase;
    padding: 0.65rem 1rem 0.3rem;
}

/* ── File list ── */
.sb-file-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 1rem;
    cursor: default;
    transition: background 0.1s;
    border-radius: 0;
}
.sb-file-item:hover { background: #F9FAFB; }
.sb-file-dot {
    width: 6px; height: 22px;
    border-radius: 3px;
    flex-shrink: 0;
}
.sb-file-name {
    font-size: 0.8rem;
    color: #374151;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
}

/* ── Divider ── */
.sb-rule {
    height: 1px;
    background: #F3F4F6;
    margin: 0.4rem 0;
}

/* ── Status chips ── */
.status-chip {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.25rem 0.6rem;
    border-radius: 20px;
    font-size: 0.7rem; font-weight: 500;
    margin: 0.2rem 0;
}
.chip-blue  { background: #EEF2FF; color: #3B5BDB; border: 1px solid #C5D0FF; }
.chip-green { background: #F0FDF4; color: #059669; border: 1px solid #A7F3D0; }

/* ── Temp row ── */
.temp-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0 0.2rem;
}
.temp-label { font-size: 0.73rem; color: #6B7280; font-weight: 500; }
.temp-val {
    font-size: 0.7rem; font-weight: 700; color: #4F7BFF;
    background: #EEF2FF; padding: 0.1rem 0.38rem; border-radius: 4px;
}

/* ── Footer item (model / settings row) ── */
.sb-footer-item {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1rem;
    font-size: 0.81rem; color: #374151; font-weight: 500;
    cursor: pointer;
    transition: background 0.1s;
}
.sb-footer-item:hover { background: #F9FAFB; }
.sb-footer-icon { font-size: 0.8rem; color: #9CA3AF; }


/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
.stButton > button {
    border-radius: 9px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    letter-spacing: -0.1px !important;
}

/* Primary */
.stButton > button[kind="primary"] {
    background: #4F7BFF !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 0.58rem 1rem !important;
    box-shadow: 0 2px 8px rgba(79,123,255,0.28) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3A68F0 !important;
    box-shadow: 0 4px 14px rgba(79,123,255,0.38) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"]:active  { transform: translateY(0) !important; }
.stButton > button[kind="primary"]:disabled {
    background: #A5BEFF !important;
    box-shadow: none !important; transform: none !important;
}

/* Secondary */
.stButton > button:not([kind="primary"]) {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #374151 !important;
    padding: 0.45rem 0.8rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: #F9FAFB !important;
    border-color: #D1D5DB !important;
    color: #111827 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07) !important;
}
.stButton > button:not([kind="primary"]):disabled { opacity: 0.4 !important; }

/* Suggestion chip buttons (marked by JS) */
.dm-chip {
    border-radius: 22px !important;
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #374151 !important;
    font-size: 0.81rem !important;
    padding: 0.48rem 0.9rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    text-align: left !important;
    white-space: nowrap !important;
}
.dm-chip:hover {
    background: #EEF2FF !important;
    border-color: #4F7BFF !important;
    color: #4F7BFF !important;
    box-shadow: 0 3px 10px rgba(79,123,255,0.14) !important;
    transform: translateY(-1px) !important;
}


/* ══════════════════════════════════════════
   WELCOME (no docs loaded yet)
══════════════════════════════════════════ */
.welcome-outer {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 1rem 2rem;
    text-align: center;
}
.welcome-icon-ring {
    width: 84px; height: 84px;
    background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem;
    margin: 0 auto 1.25rem;
    box-shadow: 0 4px 20px rgba(79,123,255,0.12);
}
.welcome-title {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
    letter-spacing: -0.3px !important;
    margin-bottom: 0.45rem !important;
}
.welcome-sub {
    font-size: 0.86rem;
    color: #6B7280;
    max-width: 340px;
    margin: 0 auto;
    line-height: 1.6;
}


/* ══════════════════════════════════════════
   WORKSPACE EMPTY STATE (docs loaded, no msgs)
══════════════════════════════════════════ */
.ws-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2.5rem 1rem 1.75rem;
    text-align: center;
}
.ws-robot {
    width: 180px; height: 170px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1.5rem;
}
.ws-robot svg { width: 160px; height: auto; }
.ws-empty-title {
    font-size: 1.22rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
    letter-spacing: -0.3px !important;
    margin-bottom: 0.4rem !important;
}
.ws-empty-sub {
    font-size: 0.84rem;
    color: #6B7280;
    margin-bottom: 1.75rem;
}


/* ══════════════════════════════════════════
   WORKSPACE BAR
══════════════════════════════════════════ */
.ws-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.65rem 1rem;
    background: #FFFFFF;
    border: 1px solid #E9ECF2;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.ws-bar-left  { display: flex; align-items: center; gap: 0.45rem; }
.ws-bar-right { display: flex; align-items: center; gap: 0.4rem; }
.ws-bar-icon  { font-size: 1rem; }
.ws-bar-title { font-size: 0.87rem; font-weight: 700; color: #111827; }
.ws-chip {
    font-size: 0.67rem; font-weight: 600; color: #6B7280;
    background: #F9FAFB; border: 1px solid #E5E7EB;
    padding: 0.17rem 0.48rem; border-radius: 16px;
}


/* ══════════════════════════════════════════
   CHAT MESSAGES — force light on all nodes
══════════════════════════════════════════ */
[data-testid="stChatMessage"],
[data-testid="stChatMessage"] > div,
[data-testid="stChatMessage"] > div > div,
[data-testid="stChatMessageContent"] {
    background: #FFFFFF !important;
    color: #1A202C !important;
}
[data-testid="stChatMessage"] {
    border: 1px solid #F0F2F5 !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.1rem !important;
    margin-bottom: 0.6rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    transition: box-shadow 0.12s !important;
}
[data-testid="stChatMessage"]:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span:not([data-testid]) {
    color: #1A202C !important;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    background: #EEF2FF !important;
    color: #4F7BFF !important;
    border: 1px solid #C5D0FF !important;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    border: 1.5px solid #E5E7EB !important;
    border-radius: 12px !important;
    font-size: 0.88rem !important;
    font-family: 'Inter', sans-serif !important;
    color: #1A202C !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #4F7BFF !important;
    box-shadow: 0 0 0 3px rgba(79,123,255,0.1), 0 2px 8px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #9CA3AF !important; }


/* ══════════════════════════════════════════
   RIGHT PANEL — SOURCES
══════════════════════════════════════════ */
.rp-wrap {
    background: #FFFFFF;
    border: 1px solid #E9ECF2;
    border-radius: 14px;
    padding: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.rp-top-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.85rem;
}
.rp-title {
    font-size: 0.87rem; font-weight: 700; color: #111827;
    display: flex; align-items: center; gap: 0.35rem;
}
.rp-more {
    font-size: 0.68rem; color: #9CA3AF;
    background: #F9FAFB; border: 1px solid #E5E7EB;
    border-radius: 5px; padding: 0.18rem 0.45rem; cursor: pointer;
}

/* Source card */
.src-card {
    background: #FFFFFF;
    border: 1px solid #E9ECF2;
    border-radius: 10px;
    padding: 0.72rem 0.8rem;
    margin-bottom: 0.55rem;
    transition: box-shadow 0.15s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.src-card:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    border-color: #D1D5DB;
}
.src-filename {
    font-size: 0.79rem; font-weight: 700; color: #111827;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    margin-bottom: 0.18rem;
}
.src-page {
    font-size: 0.68rem; color: #6B7280; font-weight: 500;
    margin-bottom: 0.38rem;
}
.src-rel-row {
    display: flex; align-items: center; gap: 0.45rem;
    margin-bottom: 0.45rem;
}
.src-rel-track {
    flex: 1; height: 5px;
    background: #F3F4F6; border-radius: 99px; overflow: hidden;
}
.src-rel-fill {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #4F7BFF 0%, #7C3AED 100%);
}
.src-rel-pct {
    font-size: 0.66rem; font-weight: 700; color: #4F7BFF;
    min-width: 28px; text-align: right;
}
.src-thumb {
    background: #F9FAFB;
    border: 1px solid #F0F2F5;
    border-radius: 6px;
    height: 46px;
    margin-bottom: 0.45rem;
    display: flex; align-items: center; justify-content: center;
}
.src-thumb-lines { display: flex; flex-direction: column; gap: 4px; width: 72%; }
.src-thumb-line  { height: 4px; background: #E5E7EB; border-radius: 99px; }
.src-excerpt {
    font-size: 0.71rem; color: #6B7280; line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 0.38rem;
}
.src-expand {
    font-size: 0.68rem; color: #4F7BFF; font-weight: 600;
    cursor: pointer; float: right; margin-top: -2px;
}

/* Panel empty state */
.rp-empty {
    text-align: center; padding: 1.5rem 0.75rem;
    border: 1.5px dashed #E5E7EB;
    border-radius: 10px; background: #F9FAFB;
}
.rp-empty-icon { font-size: 1.4rem; margin-bottom: 0.45rem; }
.rp-empty-text { font-size: 0.72rem; color: #9CA3AF; line-height: 1.55; }

/* Retrieved footer */
.rp-retrieved {
    display: flex; align-items: center; gap: 0.38rem;
    padding: 0.65rem 0.1rem 0;
    font-size: 0.71rem; color: #6B7280; font-weight: 500;
    border-top: 1px solid #F3F4F6;
    margin-top: 0.35rem;
}
.rp-retrieved strong { color: #374151; }

.rp-rule { height: 1px; background: #F3F4F6; margin: 0.7rem 0; }

/* Session stats */
.rp-heading {
    font-size: 0.71rem; font-weight: 700; color: #6B7280;
    letter-spacing: 0.02em; margin-bottom: 0.55rem;
    display: flex; align-items: center; gap: 0.3rem;
}
.stat-block {
    background: #F9FAFB; border: 1px solid #F3F4F6;
    border-radius: 8px; overflow: hidden;
}
.stat-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.36rem 0.65rem; border-bottom: 1px solid #F3F4F6;
}
.stat-row:last-child { border-bottom: none; }
.stat-key { font-size: 0.67rem; color: #9CA3AF; font-weight: 500; }
.stat-val {
    font-size: 0.69rem; font-weight: 700; color: #374151;
    background: #FFFFFF; padding: 0.1rem 0.38rem;
    border-radius: 4px; border: 1px solid #E9ECF2;
    max-width: 55%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}


/* ══════════════════════════════════════════
   STREAMLIT COMPONENT OVERRIDES
══════════════════════════════════════════ */

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
    border: 1px solid #E5E7EB !important;
    background: #FFFFFF !important;
    font-size: 0.82rem !important;
    color: #374151 !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #4F7BFF !important;
    box-shadow: 0 0 0 3px rgba(79,123,255,0.1) !important;
}

/* Slider */
[data-testid="stSlider"] [role="slider"] {
    background: #4F7BFF !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: 0 0 0 2px #4F7BFF !important;
}
[data-testid="stSlider"] > div > div > div > div { background: #4F7BFF !important; }

/* File uploader */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzoneInstructions"] {
    background: #FAFBFF !important;
    color: #6B7280 !important;
}
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed #D1D5DB !important;
    border-radius: 10px !important;
    transition: all 0.18s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] > div:hover {
    border-color: #4F7BFF !important;
    background: #EEF2FF !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] p,
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #6B7280 !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #4F7BFF, #7C3AED) !important;
    border-radius: 99px !important;
}
.stProgress > div > div {
    border-radius: 99px !important;
    background: #EEF2F8 !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.83rem !important;
    border: none !important;
}

/* Scrollbar */
::-webkit-scrollbar       { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }


/* ══════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
.ws-empty, .rp-wrap, .ws-bar, .src-card, .welcome-outer {
    animation: fadeUp 0.28s ease both;
}

</style>
"""
