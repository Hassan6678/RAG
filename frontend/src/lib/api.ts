/**
 * API client — all backend calls go through here.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Source {
  filename: string;
  page: string;
  relevance: number;
  excerpt: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
}

export interface SessionInfo {
  model: string;
  temperature: number;
  doc_count: number;
  doc_names: string[];
  message_count: number;
  has_chain: boolean;
}

export interface ModelsResponse {
  models: string[];
  default: string;
}

// ---------------------------------------------------------------------------
// Fetch with timeout helper
// ---------------------------------------------------------------------------

async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = 10_000
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/health`, {}, 5_000);
    return res.ok;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Models
// ---------------------------------------------------------------------------

export async function getModels(): Promise<ModelsResponse> {
  const res = await fetchWithTimeout(`${API_BASE}/api/models`, {}, 5_000);
  if (!res.ok) throw new Error("Failed to fetch models");
  return res.json();
}

// ---------------------------------------------------------------------------
// Upload
// ---------------------------------------------------------------------------

export async function uploadFiles(
  sessionId: string,
  files: File[]
): Promise<{ uploaded: string[]; message: string }> {
  const form = new FormData();
  form.append("session_id", sessionId);
  files.forEach((f) => form.append("files", f));

  const res = await fetchWithTimeout(
    `${API_BASE}/api/upload`,
    { method: "POST", body: form },
    30_000
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Index — embedding can take several minutes for large PDFs
// ---------------------------------------------------------------------------

export async function indexDocuments(
  sessionId: string,
  model: string,
  temperature: number
): Promise<{ indexed: number; model: string; message: string }> {
  const res = await fetchWithTimeout(
    `${API_BASE}/api/index`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, model, temperature }),
    },
    600_000 // 10 min — first-time embedding is slow on large docs
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Indexing failed" }));
    throw new Error(err.detail || "Indexing failed");
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Chat — LLM inference can take 30–120s on CPU
// ---------------------------------------------------------------------------

export async function sendMessage(
  sessionId: string,
  question: string
): Promise<ChatResponse> {
  const res = await fetchWithTimeout(
    `${API_BASE}/api/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, question }),
    },
    300_000 // 5 min
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Chat failed" }));
    throw new Error(err.detail || "Chat failed");
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Sources
// ---------------------------------------------------------------------------

export async function getSources(sessionId: string): Promise<Source[]> {
  const res = await fetchWithTimeout(
    `${API_BASE}/api/sources?session_id=${sessionId}`,
    {},
    5_000
  );
  if (!res.ok) return [];
  const data = await res.json();
  return data.sources || [];
}

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------

export async function getSessionInfo(sessionId: string): Promise<SessionInfo> {
  const res = await fetchWithTimeout(
    `${API_BASE}/api/session?session_id=${sessionId}`,
    {},
    5_000
  );
  if (!res.ok) throw new Error("Failed to get session info");
  return res.json();
}

export async function clearSession(sessionId: string): Promise<void> {
  await fetchWithTimeout(
    `${API_BASE}/api/clear`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    },
    5_000
  ).catch(() => {});
}
