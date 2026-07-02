"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { rfcs } from "@/data/rfcs";
import { specs } from "@/data/specs";
import { GlassCard, GlowingBadge } from "@/components/ui-components";

export default function RFCDetailPage() {
  const { id } = useParams();
  const rfc = rfcs.find((r) => r.id === id) || rfcs[0];
  const relatedSpecs = specs.filter((s) => s.rfc === rfc.id);

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-5xl mx-auto space-y-8">
      
      <Link href="/rfc-explorer" className="inline-flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
        <ArrowLeft className="h-4 w-4" />
        Back to Index
      </Link>

      <GlassCard hoverEffect={false} className="p-8 space-y-6">
        <div className="flex justify-between items-start border-b border-zinc-900/60 pb-6">
          <div className="space-y-1">
            <span className="text-indigo-400 text-xs font-mono font-bold">{rfc.id} Specification</span>
            <h1 className="text-2xl md:text-3xl font-extrabold text-zinc-50">{rfc.title}</h1>
          </div>
          <GlowingBadge label={rfc.status} variant={rfc.status === "RATIFIED" ? "success" : "warning"} />
        </div>

        <div className="space-y-6 text-sm">
          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Scope Description</span>
            <p className="text-zinc-300 leading-relaxed">{rfc.purpose}</p>
          </div>

          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Best Practices</span>
            <ul className="list-disc list-inside text-zinc-400 space-y-1">
              {rfc.bestPractices.map((bp, idx) => <li key={idx}>{bp}</li>)}
            </ul>
          </div>

          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Anti-Patterns</span>
            <ul className="list-disc list-inside text-rose-400/80 space-y-1">
              {rfc.antiPatterns.map((ap, idx) => <li key={idx}>{ap}</li>)}
            </ul>
          </div>

          <div className="space-y-3">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Related System SPECs</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {relatedSpecs.map((spec) => (
                <Link
                  key={spec.id}
                  href={`/specs/\${spec.id}`}
                  className="p-3 bg-zinc-950/30 border border-zinc-900/60 hover:border-zinc-800 rounded-lg flex justify-between items-center group transition-all"
                >
                  <div className="flex flex-col">
                    <span className="text-[11px] font-bold font-mono group-hover:text-indigo-400">{spec.id}</span>
                    <span className="text-[10px] text-zinc-500 truncate max-w-[180px]">{spec.title}</span>
                  </div>
                  <GlowingBadge label={spec.layer} variant="info" className="text-[9px]" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </GlassCard>

    </div>
  );
}
