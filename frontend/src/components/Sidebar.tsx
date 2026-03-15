"use client";

import { useState } from "react";

interface SidebarProps {
  models: string[];
  selectedModel: string;
  temperature: number;
  docNames: string[];
  isIndexed: boolean;
  isProcessing: boolean;
  onModelChange: (model: string) => void;
  onTemperatureChange: (temp: number) => void;
  onUpload: (files: File[]) => void;
  onProcess: () => void;
  onNewChat: () => void;
}

export default function Sidebar({
  models,
  selectedModel,
  temperature,
  docNames,
  isIndexed,
  isProcessing,
  onModelChange,
  onTemperatureChange,
  onUpload,
  onProcess,
  onNewChat,
}: SidebarProps) {
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    const pdfs = Array.from(fileList).filter((f) =>
      f.name.toLowerCase().endsWith(".pdf")
    );
    if (pdfs.length) onUpload(pdfs);
  };

  return (
    <aside className="w-[280px] min-w-[280px] h-screen bg-white border-r border-gray-200 flex flex-col overflow-hidden">
      {/* ── Brand header ── */}
      <div className="flex items-center gap-2.5 px-5 py-4 border-b border-gray-100">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
          D
        </div>
        <span className="text-[15px] font-bold text-gray-900 tracking-tight">
          DocMind AI
        </span>
      </div>

      {/* ── New Chat ── */}
      <div className="px-4 pt-4 pb-2">
        <button
          onClick={onNewChat}
          className="w-full py-2.5 rounded-lg bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-all shadow-sm hover:shadow-md flex items-center justify-center gap-2"
        >
          <span className="text-lg leading-none">+</span> New Chat
        </button>
      </div>

      {/* ── Documents section ── */}
      <div className="flex-1 overflow-y-auto px-4">
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-4 mb-2">
          Documents
        </p>

        {/* Indexed files list */}
        {docNames.length > 0 && (
          <div className="mb-3 space-y-0.5">
            {docNames.map((name, i) => (
              <div
                key={i}
                className="flex items-center gap-2.5 py-1.5 px-2 rounded-md hover:bg-gray-50 transition-colors"
              >
                <div className="w-1 h-5 rounded-full bg-red-400 flex-shrink-0" />
                <span className="text-[13px] text-gray-700 font-medium truncate">
                  {name}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Upload dropzone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFiles(e.dataTransfer.files);
          }}
          className={`
            border-2 border-dashed rounded-xl p-5 text-center transition-all cursor-pointer mb-3
            ${dragOver
              ? "border-brand-500 bg-brand-50"
              : "border-gray-200 bg-gray-50/50 hover:border-brand-400 hover:bg-brand-50/30"
            }
          `}
        >
          <p className="text-sm font-semibold text-gray-800 mb-0.5">
            Drag and drop files here
          </p>
          <p className="text-xs text-gray-400 mb-3">Limit 200MB per file &bull; PDF</p>
          <label className="inline-block px-4 py-2 bg-gray-900 text-white text-xs font-semibold rounded-lg cursor-pointer hover:bg-gray-800 transition-colors">
            Browse files
            <input
              type="file"
              accept=".pdf"
              multiple
              className="hidden"
              onChange={(e) => handleFiles(e.target.files)}
            />
          </label>
        </div>

        {/* Status + Process button */}
        {docNames.length > 0 && !isIndexed && (
          <div className="mb-3">
            <p className="text-xs text-brand-600 font-medium mb-2">
              📄 {docNames.length} file(s) selected
            </p>
            <button
              onClick={onProcess}
              disabled={isProcessing}
              className="w-full py-2.5 rounded-lg bg-gradient-to-r from-brand-500 to-purple-500 hover:from-brand-600 hover:to-purple-600 text-white text-sm font-semibold transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Processing...
                </span>
              ) : (
                "⚡ Process Documents"
              )}
            </button>
          </div>
        )}

        {isIndexed && (
          <p className="text-xs text-emerald-600 font-medium mb-2">
            ✅ {docNames.length} document(s) indexed
          </p>
        )}
      </div>

      {/* ── Model selector + Settings ── */}
      <div className="border-t border-gray-100 px-4 py-3 space-y-3">
        <div>
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
          >
            {models.map((m) => (
              <option key={m} value={m}>
                🦙 {m}
              </option>
            ))}
          </select>
        </div>
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-500 font-medium">Temperature</span>
            <span className="text-xs font-bold text-brand-500 bg-brand-50 px-1.5 py-0.5 rounded">
              {temperature.toFixed(2)}
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={temperature}
            onChange={(e) => onTemperatureChange(parseFloat(e.target.value))}
            className="w-full h-1.5 rounded-full appearance-none bg-gray-200 accent-brand-500"
          />
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400 pt-1">
          <span>⚙️</span>
          <span>Settings</span>
        </div>
      </div>
    </aside>
  );
}
