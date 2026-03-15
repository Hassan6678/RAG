"use client";

import { Source } from "@/lib/api";

interface SourcesPanelProps {
  sources: Source[];
  model: string;
  temperature: number;
  docCount: number;
}

function RelevanceBar({ pct }: { pct: number }) {
  return (
    <div className="flex items-center gap-2 mb-2">
      <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-brand-500 to-purple-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[11px] font-bold text-brand-500 min-w-[28px] text-right">
        {pct}%
      </span>
    </div>
  );
}

function TextPlaceholder() {
  return (
    <div className="bg-gray-50 border border-gray-100 rounded-md h-12 mb-2 flex items-center justify-center">
      <div className="flex flex-col gap-1 w-3/4">
        <div className="h-1 bg-gray-200 rounded-full w-full" />
        <div className="h-1 bg-gray-200 rounded-full w-4/5" />
        <div className="h-1 bg-gray-200 rounded-full w-11/12" />
        <div className="h-1 bg-gray-200 rounded-full w-3/5" />
      </div>
    </div>
  );
}

function SourceCard({ source }: { source: Source }) {
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-3 mb-2.5 shadow-sm hover:shadow-md hover:border-gray-200 transition-all">
      <p className="text-[13px] font-bold text-gray-900 truncate mb-0.5">
        {source.filename}
      </p>
      {source.page && (
        <p className="text-[11px] text-gray-500 font-medium mb-1.5">
          {source.page}
        </p>
      )}
      <RelevanceBar pct={source.relevance} />
      <TextPlaceholder />
      <p className="text-[11px] text-gray-500 leading-relaxed line-clamp-3 mb-1.5">
        {source.excerpt}
      </p>
      <span className="text-[11px] text-brand-500 font-semibold cursor-pointer float-right hover:text-brand-600">
        Expand
      </span>
    </div>
  );
}

export default function SourcesPanel({
  sources,
  model,
  temperature,
  docCount,
}: SourcesPanelProps) {
  return (
    <aside className="w-[300px] min-w-[300px] h-screen bg-white border-l border-gray-200 flex flex-col overflow-hidden">
      {/* ── Header ── */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-gray-100">
        <h2 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
          📑 Sources
        </h2>
        <span className="text-[10px] text-gray-400 bg-gray-50 border border-gray-200 rounded px-1.5 py-0.5 cursor-pointer">
          ···
        </span>
      </div>

      {/* ── Sources list ── */}
      <div className="flex-1 overflow-y-auto px-3 py-3">
        {sources.length === 0 ? (
          <div className="text-center py-10 border-2 border-dashed border-gray-100 rounded-xl bg-gray-50/50">
            <div className="text-2xl mb-2">📄</div>
            <p className="text-xs text-gray-400 leading-relaxed">
              Sources appear here
              <br />
              after your first question
            </p>
          </div>
        ) : (
          <>
            {sources.map((s, i) => (
              <SourceCard key={i} source={s} />
            ))}
            <div className="flex items-center gap-1.5 pt-2 mt-1 border-t border-gray-100 text-xs text-gray-500">
              <span>📨</span>
              <span>
                Retrieved <strong className="text-gray-700">{sources.length}</strong>{" "}
                source{sources.length !== 1 ? "s" : ""}
              </span>
            </div>
          </>
        )}
      </div>

      {/* ── Session info ── */}
      <div className="border-t border-gray-100 px-4 py-3 space-y-3">
        <h3 className="text-[11px] font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
          ⚙️ Session
        </h3>
        <div className="bg-gray-50 border border-gray-100 rounded-lg overflow-hidden">
          {[
            ["Model", model || "—"],
            ["Temp", temperature.toFixed(2)],
            ["Docs", String(docCount)],
          ].map(([label, value]) => (
            <div
              key={label}
              className="flex justify-between items-center px-3 py-2 border-b border-gray-100 last:border-b-0"
            >
              <span className="text-[11px] text-gray-400 font-medium">{label}</span>
              <span className="text-[11px] font-bold text-gray-700 bg-white px-2 py-0.5 rounded border border-gray-100 truncate max-w-[55%]">
                {value}
              </span>
            </div>
          ))}
        </div>

        {/* Analytics placeholder */}
        <div className="mt-2">
          <div className="flex items-center gap-1.5 mb-2">
            <span className="text-xs">📊</span>
            <span className="text-[11px] font-bold text-gray-500">Analytics</span>
            <span className="text-[9px] font-bold text-amber-600 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-full ml-auto">
              SOON
            </span>
          </div>
          <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 py-2">
            <div className="flex items-center gap-1.5 text-[11px] text-gray-400">
              <span>📈</span> Key Metrics
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
