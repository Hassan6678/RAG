"""Product-level constants and data definitions."""

APP_TITLE   = "DocMind AI"
APP_ICON    = "🧠"
APP_TAGLINE = "AI Research & Analytics Workspace"

PROMPT_CHIPS = [
    "Summarize the key points",
    "What are the main findings?",
    "List all recommendations",
    "Extract key metrics",
    "What conclusions are drawn?",
    "Compare the main sections",
]

# (icon, title, description, accent-color, accent-bg, coming-soon)
CAPABILITIES = [
    ("🔍", "Semantic Search",
     "Find answers across thousands of pages using vector similarity retrieval.",
     "#2563EB", "#DBEAFE", False),
    ("🧠", "RAG Pipeline",
     "Multi-turn memory with full source attribution on every response.",
     "#7C3AED", "#EDE9FE", False),
    ("📊", "Analytics",
     "Charts, KPI cards & table views across your document data.",
     "#059669", "#D1FAE5", True),
    ("🔗", "Hybrid Queries",
     "Combine document search with structured data queries in one answer.",
     "#EA580C", "#FFEDD5", True),
]
