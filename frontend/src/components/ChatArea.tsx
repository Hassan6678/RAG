"use client";

import { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatAreaProps {
  messages: Message[];
  isIndexed: boolean;
  isLoading: boolean;
  docNames: string[];
  model: string;
  onSend: (question: string) => void;
  onChipClick: (chip: string) => void;
}

const SUGGESTION_CHIPS = [
  "Show recent sales trends",
  "Summarize the last quarter's performance",
  "List key customer feedback points",
];

// Inline robot SVG
function RobotIllustration() {
  return (
    <svg
      viewBox="0 0 220 200"
      className="w-44 h-auto mx-auto mb-6"
      xmlns="http://www.w3.org/2000/svg"
    >
      <ellipse cx="110" cy="192" rx="55" ry="6" fill="#D6DEFF" opacity="0.5" />
      <rect x="60" y="72" width="100" height="80" rx="20" fill="#E8EDFF" stroke="#B8C4FF" strokeWidth="2" />
      <rect x="76" y="88" width="68" height="40" rx="10" fill="#FFFFFF" stroke="#C5D0FF" strokeWidth="1.5" />
      <circle cx="96" cy="108" r="5" fill="#4F7BFF" opacity="0.6" />
      <circle cx="110" cy="108" r="5" fill="#7C3AED" opacity="0.5" />
      <circle cx="124" cy="108" r="5" fill="#4F7BFF" opacity="0.6" />
      <rect x="68" y="18" width="84" height="58" rx="18" fill="#D6DEFF" stroke="#A8B8FF" strokeWidth="2" />
      <ellipse cx="92" cy="44" rx="10" ry="11" fill="#FFFFFF" stroke="#A8B8FF" strokeWidth="1.5" />
      <ellipse cx="128" cy="44" rx="10" ry="11" fill="#FFFFFF" stroke="#A8B8FF" strokeWidth="1.5" />
      <circle cx="94" cy="43" r="5" fill="#4F7BFF" />
      <circle cx="130" cy="43" r="5" fill="#4F7BFF" />
      <circle cx="96" cy="41" r="2" fill="#FFFFFF" />
      <circle cx="132" cy="41" r="2" fill="#FFFFFF" />
      <path d="M96 56 Q110 66 124 56" fill="none" stroke="#4F7BFF" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="110" y1="18" x2="110" y2="6" stroke="#A8B8FF" strokeWidth="3" strokeLinecap="round" />
      <circle cx="110" cy="4" r="5" fill="#4F7BFF" />
      <rect x="34" y="86" width="28" height="14" rx="7" fill="#D6DEFF" stroke="#A8B8FF" strokeWidth="1.5" />
      <rect x="158" y="86" width="28" height="14" rx="7" fill="#D6DEFF" stroke="#A8B8FF" strokeWidth="1.5" />
      <circle cx="34" cy="93" r="7" fill="#C5D0FF" stroke="#A8B8FF" strokeWidth="1.5" />
      <circle cx="186" cy="93" r="7" fill="#C5D0FF" stroke="#A8B8FF" strokeWidth="1.5" />
      <rect x="80" y="152" width="18" height="24" rx="8" fill="#D6DEFF" stroke="#A8B8FF" strokeWidth="1.5" />
      <rect x="122" y="152" width="18" height="24" rx="8" fill="#D6DEFF" stroke="#A8B8FF" strokeWidth="1.5" />
      <rect x="74" y="170" width="30" height="14" rx="7" fill="#C5D0FF" stroke="#A8B8FF" strokeWidth="1.5" />
      <rect x="116" y="170" width="30" height="14" rx="7" fill="#C5D0FF" stroke="#A8B8FF" strokeWidth="1.5" />
      <rect x="56" y="32" width="12" height="20" rx="6" fill="#C5D0FF" stroke="#A8B8FF" strokeWidth="1.5" />
      <rect x="152" y="32" width="12" height="20" rx="6" fill="#C5D0FF" stroke="#A8B8FF" strokeWidth="1.5" />
    </svg>
  );
}

export default function ChatArea({
  messages,
  isIndexed,
  isLoading,
  docNames,
  model,
  onSend,
  onChipClick,
}: ChatAreaProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = () => {
    const q = input.trim();
    if (!q || isLoading) return;
    setInput("");
    onSend(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // ── Welcome state (no docs indexed) ──
  if (!isIndexed) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-brand-50 to-purple-50 flex items-center justify-center text-4xl mb-5 shadow-lg shadow-brand-500/10">
          🧠
        </div>
        <h1 className="text-xl font-bold text-gray-900 mb-2">Welcome to DocMind AI</h1>
        <p className="text-sm text-gray-500 max-w-xs text-center leading-relaxed">
          Upload PDF documents in the sidebar and click{" "}
          <strong>Process Documents</strong> to build your knowledge base.
        </p>
      </div>
    );
  }

  // ── Empty state (docs indexed, no messages) ──
  const showEmpty = messages.length === 0;

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* ── Top bar ── */}
      <div className="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-base">🧠</span>
          <span className="text-sm font-bold text-gray-900">DocMind AI</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-gray-500 bg-gray-50 border border-gray-200 px-2 py-0.5 rounded-full">
            {model}
          </span>
          <span className="text-[11px] font-semibold text-gray-500 bg-gray-50 border border-gray-200 px-2 py-0.5 rounded-full">
            📚 {docNames.length} doc{docNames.length !== 1 ? "s" : ""}
          </span>
        </div>
      </div>

      {/* ── Messages area ── */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        {showEmpty ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <RobotIllustration />
            <h2 className="text-lg font-bold text-gray-900 mb-1">
              Ask questions about your documents 📄
            </h2>
            <p className="text-sm text-gray-500 mb-6">
              Ask anything about the documents you&apos;ve uploaded
            </p>
            <div className="flex flex-wrap justify-center gap-2 max-w-lg">
              {SUGGESTION_CHIPS.map((chip) => (
                <button
                  key={chip}
                  onClick={() => onChipClick(chip)}
                  className="px-4 py-2.5 text-sm text-gray-700 bg-white border border-gray-200 rounded-full hover:border-brand-500 hover:text-brand-600 hover:bg-brand-50/50 transition-all shadow-sm hover:shadow-md"
                >
                  {chip} <span className="text-gray-300 ml-1">›</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-brand-50 border border-brand-200 flex items-center justify-center text-sm flex-shrink-0 mt-0.5">
                    🧠
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-brand-500 text-white rounded-br-md"
                      : "bg-white border border-gray-100 text-gray-800 rounded-bl-md shadow-sm"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
                        li: ({ children }) => <li className="mb-1">{children}</li>,
                        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                        code: ({ children }) => (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">
                            {children}
                          </code>
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-sm flex-shrink-0 mt-0.5">
                    👤
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-50 border border-brand-200 flex items-center justify-center text-sm flex-shrink-0">
                  🧠
                </div>
                <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* ── Input bar ── */}
      <div className="px-5 py-3 bg-white border-t border-gray-100">
        <div className="flex items-end gap-2 bg-gray-50 border border-gray-200 rounded-xl p-1.5 focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/10 transition-all">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            rows={1}
            disabled={!isIndexed || isLoading}
            className="flex-1 bg-transparent resize-none text-sm text-gray-800 placeholder-gray-400 px-3 py-2 focus:outline-none disabled:opacity-50 max-h-32"
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading || !isIndexed}
            className="w-9 h-9 rounded-lg bg-brand-500 hover:bg-brand-600 text-white flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
