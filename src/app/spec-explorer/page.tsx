"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, Database, ChevronRight } from "lucide-react";
import { specs } from "@/data/specs";
import { GlassCard, GlowingBadge, SectionHeader } from "@/components/ui-components";

export default function SPECExplorer() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLayer, setSelectedLayer] = useState("All");
  const [selectedSpec, setSelectedSpec] = useState(specs[0]);

  const layers = ["All", "Intelligence", "Execution", "Runtime", "Learning", "Enterprise"];

  const filteredSpecs = specs.filter((spec) => {
    const matchesSearch = 
      spec.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      spec.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      spec.purpose.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesLayer = selectedLayer === "All" || spec.layer === selectedLayer;
    return matchesSearch && matchesLayer;
  });

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12">
      
      {/* Sidebar search / filter */}
      <div className="lg:col-span-4 space-y-6">
        <SectionHeader 
          title="SPEC Explorer" 
          subtitle="Explore all 170 specifications governing the Aetheris runtime engines."
          badge="Engine SPECs"
        />

        <div className="relative">
          <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-zinc-600" />
          <input
            type="text"
            placeholder="Search SPECs (e.g. SPEC-039)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-zinc-950/60 border border-zinc-900/60 rounded-xl py-3 pl-10 pr-4 text-xs focus:outline-none focus:border-indigo-500/80 transition-all font-mono"
          />
        </div>

        <div className="flex flex-wrap gap-1.5">
          {layers.map((layer) => (
            <button
              key={layer}
              onClick={() => setSelectedLayer(layer)}
              className={`px-3 py-1.5 rounded-lg text-[10px] font-semibold border transition-all \${
                selectedLayer === layer
                  ? "bg-indigo-600/10 border-indigo-500/30 text-indigo-400"
                  : "bg-zinc-950/20 border-zinc-900/40 text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {layer}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-2 max-h-[350px] overflow-y-auto pr-1">
          {filteredSpecs.map((spec) => (
            <button
              key={spec.id}
              onClick={() => setSelectedSpec(spec)}
              className={`w-full text-left p-3.5 rounded-xl border flex items-center justify-between transition-all \${
                selectedSpec.id === spec.id
                  ? "bg-indigo-600/10 border-indigo-500/30 text-indigo-400"
                  : "bg-zinc-950/20 border-zinc-900/60 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-bold font-mono">{spec.id}</span>
                <span className="text-[10px] text-zinc-500 truncate max-w-[200px]">{spec.title}</span>
              </div>
              <span className="text-[8px] font-mono px-2 py-0.5 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-500">
                {spec.layer}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Detail Pane */}
      <div className="lg:col-span-8">
        <GlassCard hoverEffect={false} className="space-y-6 p-8 h-full flex flex-col justify-between">
          <div className="space-y-6">
            <div className="border-b border-zinc-900/60 pb-4 flex justify-between items-center">
              <div>
                <span className="text-indigo-400 text-xs font-mono font-bold">{selectedSpec.id}</span>
                <h2 className="text-xl md:text-2xl font-extrabold text-zinc-50">{selectedSpec.title}</h2>
              </div>
              <GlowingBadge label={selectedSpec.layer} variant="info" />
            </div>

            <div className="space-y-4 text-xs leading-relaxed">
              <div className="space-y-1">
                <span className="text-zinc-500 font-mono uppercase tracking-wider block text-[10px]">Purpose</span>
                <p className="text-zinc-300">{selectedSpec.purpose}</p>
              </div>

              <div className="space-y-1">
                <span className="text-zinc-500 font-mono uppercase tracking-wider block text-[10px]">Responsibilities</span>
                <p className="text-zinc-400">{selectedSpec.responsibilities}</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <span className="text-zinc-500 font-mono uppercase tracking-wider block text-[10px]">Input Parameters</span>
                  <p className="text-zinc-400 font-mono bg-zinc-950/40 p-2 rounded border border-zinc-900/60">{selectedSpec.inputs}</p>
                </div>
                <div className="space-y-1">
                  <span className="text-zinc-500 font-mono uppercase tracking-wider block text-[10px]">Output Guarantee</span>
                  <p className="text-zinc-400 font-mono bg-zinc-950/40 p-2 rounded border border-zinc-900/60">{selectedSpec.outputs}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-zinc-900/60 flex justify-between items-center">
            <span className="text-[10px] text-zinc-500 font-mono">Source: {selectedSpec.source}</span>
            <Link
              href={`/specs/\${selectedSpec.id}`}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            >
              View Reference
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        </GlassCard>
      </div>

    </div>
  );
}
