"use client";

import React, { useState } from "react";
import Link from "next/link";
import { FileText, ChevronRight } from "lucide-react";
import { rfcs } from "@/data/rfcs";
import { GlassCard, GlowingBadge, SectionHeader } from "@/components/ui-components";

export default function RFCExplorer() {
  const [selectedRfc, setSelectedRfc] = useState(rfcs[0]);

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12">
      
      {/* Sidebar Selector */}
      <div className="lg:col-span-4 space-y-6">
        <SectionHeader 
          title="RFC Explorer" 
          subtitle="Explore the architecture specifications driving Aetheris subsystems."
          badge="RFC Specifications"
        />

        <div className="flex flex-col gap-2 max-h-[500px] overflow-y-auto pr-1">
          {rfcs.map((rfc) => (
            <button
              key={rfc.id}
              onClick={() => setSelectedRfc(rfc)}
              className={`w-full text-left p-3.5 rounded-xl border flex items-center justify-between transition-all \${
                selectedRfc.id === rfc.id
                  ? "bg-indigo-600/10 border-indigo-500/30 text-indigo-400"
                  : "bg-zinc-950/20 border-zinc-900/60 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4" />
                <div className="flex flex-col">
                  <span className="text-xs font-bold font-mono">{rfc.id}</span>
                  <span className="text-[10px] text-zinc-500 truncate max-w-[180px]">{rfc.title}</span>
                </div>
              </div>
              <GlowingBadge label={rfc.status} variant={rfc.status === "RATIFIED" ? "success" : "warning"} />
            </button>
          ))}
        </div>
      </div>

      {/* Content pane */}
      <div className="lg:col-span-8">
        <GlassCard hoverEffect={false} className="space-y-6 p-8 h-full flex flex-col justify-between">
          <div className="space-y-6">
            <div className="border-b border-zinc-900/60 pb-4">
              <span className="text-indigo-400 text-xs font-mono font-bold">{selectedRfc.id}</span>
              <h2 className="text-xl md:text-2xl font-extrabold text-zinc-50">{selectedRfc.title}</h2>
            </div>

            <div className="space-y-4 text-xs">
              <div className="space-y-1">
                <span className="text-zinc-500 font-mono uppercase tracking-wider block text-[10px]">Purpose</span>
                <p className="text-zinc-300 leading-relaxed font-sans">{selectedRfc.purpose}</p>
              </div>

              <div className="space-y-1">
                <span className="text-zinc-500 font-mono uppercase tracking-wider block text-[10px]">Governed Modules</span>
                <ul className="list-disc list-inside text-zinc-400 space-y-1 font-sans">
                  {selectedRfc.modules.map((m, idx) => <li key={idx}>{m}</li>)}
                </ul>
              </div>

              <div className="space-y-1">
                <span className="text-zinc-500 font-mono uppercase tracking-wider block text-[10px]">System Architecture Details</span>
                <p className="text-zinc-400 leading-relaxed font-sans">{selectedRfc.architecture}</p>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-zinc-900/60 flex justify-between items-center">
            <div className="flex gap-2">
              {selectedRfc.dependencies.map((dep, idx) => (
                <span key={idx} className="bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono text-[9px] px-2 py-1 rounded">
                  Depends: {dep}
                </span>
              ))}
            </div>
            <Link
              href={`/rfcs/\${selectedRfc.id}`}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            >
              Detailed Specs
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        </GlassCard>
      </div>

    </div>
  );
}
