# DocMind AI

Local RAG (Retrieval-Augmented Generation) workspace — upload PDFs, build a vector index, and chat with your documents. Fully local, zero paid API usage.

**Stack:** FastAPI · Next.js · Ollama · FAISS · LangChain · Docker

---

## Architecture

```
bot/
├── backend/          # FastAPI + RAG logic
│   ├── app/
│   │   ├── api/      # Routes (upload, index, chat, sources)
│   │   ├── core/     # Config
│   │   ├── schemas/  # Pydantic models
│   │   └── services/ # RAG pipeline service
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # Next.js + Tailwind
│   ├── src/
│   │   ├── app/      # Pages + layout
│   │   ├── components/ # Sidebar, ChatArea, SourcesPanel
│   │   └── lib/      # API client
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

| Method | Path            | Description                    |
|--------|-----------------|--------------------------------|
| GET    | `/health`       | Backend health check           |
| GET    | `/api/models`   | List available Ollama models   |
| POST   | `/api/upload`   | Upload PDF files               |
| POST   | `/api/index`    | Build FAISS index from uploads |
| POST   | `/api/chat`     | Ask a question                 |
| GET    | `/api/sources`  | Get last retrieved sources     |
| GET    | `/api/session`  | Session info                   |
| POST   | `/api/clear`    | Clear/reset session            |

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) running locally

### 1. Pull the models

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## Docker (Full Stack)

```bash
# Build and start all services (Ollama + Backend + Frontend)
docker compose up --build -d

# Pull models inside the Ollama container
docker exec docmind-ollama ollama pull nomic-embed-text
docker exec docmind-ollama ollama pull llama3.2:3b
```

Open **http://localhost:3000**.

### GPU Support (NVIDIA)

The `docker-compose.yml` includes NVIDIA GPU passthrough for RTX 3050 6GB. Requirements:
- NVIDIA GPU drivers installed
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- Docker Desktop: Settings → Resources → Enable GPU

---

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

| Variable              | Default                    | Description             |
|-----------------------|----------------------------|-------------------------|
| `OLLAMA_BASE_URL`     | `http://localhost:11434`   | Ollama server URL       |
| `CACHE_DIR`           | `./.cache`                 | Upload/index storage    |
| `FRONTEND_URL`        | `http://localhost:3000`    | CORS allowed origin     |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000`    | Backend URL for frontend|

---

## How It Works

1. **Upload** — PDFs are sent to `POST /api/upload` and saved to `.cache/uploads/`
2. **Index** — `POST /api/index` splits documents into chunks, embeds with Ollama (`nomic-embed-text`), and stores in FAISS
3. **Chat** — `POST /api/chat` retrieves relevant chunks and generates answers with the selected Ollama model
4. **Sources** — Each response includes source documents with filename, page, relevance score, and excerpt

---

## Migration Notes (from Streamlit)

| What               | Before (Streamlit)           | After (FastAPI + Next.js)              |
|--------------------|------------------------------|----------------------------------------|
| UI framework       | Streamlit widgets            | React + Tailwind CSS                   |
| Backend            | Streamlit re-run loop        | FastAPI REST API                       |
| State management   | `st.session_state`           | React state + backend sessions         |
| RAG logic          | `src/logic.py`               | `backend/app/services/rag_service.py`  |
| File upload        | `st.file_uploader`           | `POST /api/upload` + drag-and-drop     |
| Chat               | `st.chat_input`              | `POST /api/chat` + React chat UI       |

The old Streamlit code (`src/`, `run.py`) is kept as legacy reference.
