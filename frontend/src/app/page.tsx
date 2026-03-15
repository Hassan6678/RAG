"use client";

import { useCallback, useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import Sidebar from "@/components/Sidebar";
import ChatArea, { Message } from "@/components/ChatArea";
import SourcesPanel from "@/components/SourcesPanel";
import {
  checkHealth,
  clearSession,
  getModels,
  indexDocuments,
  sendMessage,
  Source,
  uploadFiles,
} from "@/lib/api";

export default function Home() {
  // ── Session ──
  const [sessionId, setSessionId] = useState(() => uuidv4());

  // ── Models ──
  const [models, setModels] = useState<string[]>(["llama3.2:3b"]);
  const [selectedModel, setSelectedModel] = useState("llama3.2:3b");
  const [temperature, setTemperature] = useState(0.1);

  // ── Documents ──
  const [docNames, setDocNames] = useState<string[]>([]);
  const [isIndexed, setIsIndexed] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // ── Chat ──
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // ── Status ──
  const [error, setError] = useState<string | null>(null);
  const [backendReady, setBackendReady] = useState(false);

  // ── Init: fetch models + health check ──
  useEffect(() => {
    checkHealth().then(setBackendReady);
    getModels()
      .then((data) => {
        setModels(data.models);
        setSelectedModel(data.default);
      })
      .catch(() => {});
  }, []);

  // ── Upload handler ──
  const handleUpload = useCallback(
    async (files: File[]) => {
      setError(null);
      try {
        const result = await uploadFiles(sessionId, files);
        setDocNames((prev) => [...new Set([...prev, ...result.uploaded])]);
      } catch (e: any) {
        setError(e.message);
      }
    },
    [sessionId]
  );

  // ── Process/Index handler ──
  const handleProcess = useCallback(async () => {
    setError(null);
    setIsProcessing(true);
    try {
      await indexDocuments(sessionId, selectedModel, temperature);
      setIsIndexed(true);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsProcessing(false);
    }
  }, [sessionId, selectedModel, temperature]);

  // ── Chat handler ──
  const handleSend = useCallback(
    async (question: string) => {
      setError(null);
      setMessages((prev) => [...prev, { role: "user", content: question }]);
      setIsLoading(true);
      try {
        const result = await sendMessage(sessionId, question);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: result.answer },
        ]);
        setSources(result.sources);
      } catch (e: any) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `**Error:** ${e.message}` },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  // ── New Chat ──
  const handleNewChat = useCallback(async () => {
    await clearSession(sessionId).catch(() => {});
    const newId = uuidv4();
    setSessionId(newId);
    setMessages([]);
    setSources([]);
    setDocNames([]);
    setIsIndexed(false);
    setError(null);
  }, [sessionId]);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* ── Left sidebar ── */}
      <Sidebar
        models={models}
        selectedModel={selectedModel}
        temperature={temperature}
        docNames={docNames}
        isIndexed={isIndexed}
        isProcessing={isProcessing}
        onModelChange={setSelectedModel}
        onTemperatureChange={setTemperature}
        onUpload={handleUpload}
        onProcess={handleProcess}
        onNewChat={handleNewChat}
      />

      {/* ── Main chat area ── */}
      <main className="flex-1 flex flex-col min-h-0 bg-[#F0F4F8]">
        {/* Error banner */}
        {error && (
          <div className="mx-5 mt-3 px-4 py-2.5 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-600 ml-3 text-lg leading-none"
            >
              &times;
            </button>
          </div>
        )}
        {/* Backend status */}
        {!backendReady && (
          <div className="mx-5 mt-3 px-4 py-2.5 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-700">
            Backend not reachable. Make sure the FastAPI server is running on port 8000.
          </div>
        )}
        <ChatArea
          messages={messages}
          isIndexed={isIndexed}
          isLoading={isLoading}
          docNames={docNames}
          model={selectedModel}
          onSend={handleSend}
          onChipClick={handleSend}
        />
      </main>

      {/* ── Right panel ── */}
      <SourcesPanel
        sources={sources}
        model={selectedModel}
        temperature={temperature}
        docCount={docNames.length}
      />
    </div>
  );
}
