"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, X, FileText, Cpu, Database, HelpCircle } from "lucide-react";
import { searchAll, SearchResult } from "@/lib/search";

export default function CommandPalette({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close palette on Esc or clicking outside
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    setResults(searchAll(query));
  }, [query]);

  const selectItem = (item: SearchResult) => {
    router.push(item.href);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-start justify-center pt-24 px-6">
      <div 
        ref={containerRef}
        className="w-full max-w-xl bg-zinc-950/95 border border-zinc-800/80 rounded-xl overflow-hidden shadow-2xl flex flex-col"
      >
        <div className="relative border-b border-zinc-900/60 p-4">
          <Search className="absolute left-4 top-4.5 h-4 w-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Search RFCs, SPECs, skills, docs..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent pl-10 pr-10 text-zinc-100 text-sm focus:outline-none placeholder-zinc-600"
            autoFocus
          />
          <button onClick={onClose} className="absolute right-4 top-4.5 text-zinc-500 hover:text-zinc-300">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-[300px] overflow-y-auto p-2">
          {results.length > 0 ? (
            results.map((res) => (
              <button
                key={res.id}
                onClick={() => selectItem(res)}
                className="w-full text-left p-3 rounded-lg hover:bg-zinc-900/60 flex items-start gap-3 transition-colors group"
              >
                <div className="h-8 w-8 rounded bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400 group-hover:text-indigo-400">
                  {res.type === "RFC" && <FileText className="h-4 w-4" />}
                  {res.type === "SPEC" && <Database className="h-4 w-4" />}
                  {res.type === "Skill" && <Cpu className="h-4 w-4" />}
                  {res.type === "Doc" && <HelpCircle className="h-4 w-4" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-zinc-200">{res.title}</span>
                    <span className="text-[9px] font-mono text-zinc-500 uppercase">{res.type}</span>
                  </div>
                  <p className="text-[10px] text-zinc-500 truncate mt-0.5">{res.description}</p>
                </div>
              </button>
            ))
          ) : query ? (
            <div className="text-center py-8 text-zinc-500 text-xs">No matching results found.</div>
          ) : (
            <div className="text-center py-8 text-zinc-600 text-[10px] font-mono uppercase">Type to search the platform...</div>
          )}
        </div>
      </div>
    </div>
  );
}
