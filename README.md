# DocMind AI — Enterprise RAG Chatbot

> Ask questions across your PDF documents. Get accurate, source-grounded answers in seconds.

Built with **LangChain · FAISS · Streamlit** — supports **OpenAI, Claude (Anthropic), and DeepSeek** as interchangeable chat providers.

---

## What it does

Upload one or more PDF documents, choose your preferred LLM provider, and start chatting. The app retrieves the most relevant passages from your files and passes them — together with your full conversation history — to the selected model. Every response cites the exact source document and page number it was drawn from.

---

## Supported Providers

| Provider | Models | Key prefix | Get a key |
|---|---|---|---|
| **OpenAI** | gpt-4o-mini, gpt-3.5-turbo, gpt-4o | `sk-` | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Claude (Anthropic)** | claude-3-5-haiku, claude-3-5-sonnet, claude-3-opus | `sk-ant-` | [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| **DeepSeek** | deepseek-chat, deepseek-reasoner | `sk-` | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |

> **Note on embeddings:** Regardless of which chat provider you choose, document embeddings always use OpenAI (`text-embedding-ada-002`). This keeps the FAISS vector space consistent. If you use Claude or DeepSeek for chat, you still need a separate OpenAI key for embeddings.

---

## Key Features

| Feature | Detail |
|---|---|
| Multi-provider support | Switch between OpenAI, Claude, and DeepSeek from the sidebar |
| Multi-document Q&A | Upload and query multiple PDFs in a single session |
| Persistent vector index | FAISS index cached on disk; identical file sets are never re-embedded |
| Source tracing | Each answer surfaces the document name and page number |
| Configurable LLM | Model and temperature selectable per provider |
| Multi-turn memory | Full conversation history via `ConversationBufferMemory` |
| Progress feedback | Step-by-step progress bar during document processing |
| Clean SaaS UI | Dark-themed, responsive Streamlit layout |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                   │  src/app_ui.py
│  Provider picker · API keys · Chat · Status     │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│               RAG Pipeline                      │  src/logic.py
│  PDF load → Chunk → Embed (OpenAI) → FAISS     │
│  ConversationalRetrievalChain (any provider)    │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              Utility Layer                      │  src/utils.py
│  File I/O · env loading · key validation        │
└─────────────────────────────────────────────────┘
```

---

## Tech Stack

- **LangChain 0.2** — chain orchestration and memory
- **langchain-openai** — OpenAI chat + embeddings
- **langchain-anthropic** — Claude chat
- **FAISS-CPU** — local vector similarity search
- **PyPDF** — PDF text extraction
- **Streamlit 1.36** — web UI

---

## Setup

### 1. Create a virtual environment

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your `.env` file

Create a `.env` file in the project root. Add the keys for the provider(s) you want to use:

```env
# Required for embeddings — always needed
OPENAI_API_KEY=sk-...

# Required only when using Claude for chat
ANTHROPIC_API_KEY=sk-ant-...

# Required only when using DeepSeek for chat
DEEPSEEK_API_KEY=sk-...
```

You can also paste keys directly in the sidebar at runtime — no `.env` required for quick testing.

### 4. Run the app

```bash
streamlit run run.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## How it works

1. **Choose provider** — Select OpenAI, Claude, or DeepSeek in the sidebar and enter the corresponding API key(s).
2. **Upload** — PDFs are saved to `.cache/uploads/` with UUID-prefixed filenames to prevent collisions.
3. **Index** — Documents are split into overlapping 1 200-character chunks, embedded with OpenAI, and stored in a FAISS vector database. The index is keyed by SHA-256 hash of file contents, so identical uploads skip re-embedding.
4. **Retrieve** — At query time, the question is embedded and the top-4 nearest chunks are fetched from FAISS.
5. **Generate** — Retrieved context + full conversation history are sent to the selected model.
6. **Cite** — Source document and page number are shown in a collapsible expander beneath each response.

---

## Project structure

```
bot/
├── run.py                 # Entry point
├── requirements.txt
├── .env                   # API keys (gitignored)
├── src/
│   ├── app_ui.py          # Streamlit UI (StreamlitUI class)
│   ├── logic.py           # RAG pipeline + provider registry (RAGPipeline class)
│   └── utils.py           # File I/O, env loading, key validation
└── .cache/                # Runtime cache (gitignored)
    ├── uploads/
    └── indexes/
```

---

## Notes

- `.cache/` is gitignored; uploads and indexes persist only on the local machine.
- Chat history resets when you re-process documents or click **Clear Chat**.
- Only text-based PDFs are supported. Scanned images require OCR pre-processing.
- DeepSeek uses an OpenAI-compatible API endpoint, so no extra library is needed.

---

*Portfolio demonstration — see [LICENSE](LICENSE) for usage terms.*
