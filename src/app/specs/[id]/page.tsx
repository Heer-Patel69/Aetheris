"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Code } from "lucide-react";
import { specs } from "@/data/specs";
import { GlassCard, GlowingBadge } from "@/components/ui-components";

export default function SPECDetailPage() {
  const { id } = useParams();
  const spec = specs.find((s) => s.id === id) || specs[0];

  const triggerDownload = (format: "json" | "yaml" | "md") => {
    let content = "";
    if (format === "json") {
      content = JSON.stringify(spec, null, 2);
    } else if (format === "yaml") {
      content = `---
id: \${spec.id}
title: \${spec.title}
purpose: \${spec.purpose}
layer: \${spec.layer}
...`;
    } else {
      content = `# Specification: \${spec.id} — \${spec.title}

## Purpose
\${spec.purpose}

## Layer
\${spec.layer}

## Responsibilities
\${spec.responsibilities}

## Source
\${spec.source}
`;
    }

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `\${spec.id}.\${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-4xl mx-auto space-y-8">
      
      <Link href="/spec-explorer" className="inline-flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
        <ArrowLeft className="h-4 w-4" />
        Back to Index
      </Link>

      <GlassCard hoverEffect={false} className="p-8 space-y-6">
        <div className="flex justify-between items-start border-b border-zinc-900/60 pb-6">
          <div className="space-y-1">
            <span className="text-indigo-400 text-xs font-mono font-bold">{spec.id} Engine Contract</span>
            <h1 className="text-xl md:text-2xl font-extrabold text-zinc-50">{spec.title}</h1>
          </div>
          <GlowingBadge label={spec.layer} variant="info" />
        </div>

        <div className="space-y-6 text-sm">
          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Description</span>
            <p className="text-zinc-300 leading-relaxed">{spec.purpose}</p>
          </div>

          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Core Execution Responsibilities</span>
            <p className="text-zinc-400 leading-relaxed font-sans">{spec.responsibilities}</p>
          </div>

          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">JSON Validation Schema</span>
            <pre className="bg-zinc-950 p-4 rounded-lg font-mono text-xs text-zinc-400 overflow-x-auto">
              {spec.jsonSchema}
            </pre>
          </div>

          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Recovery Plan</span>
            <p className="text-zinc-300">{spec.recoveryPlan}</p>
          </div>

          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Performance target</span>
            <p className="text-zinc-300">{spec.performanceTarget}</p>
          </div>

          <div className="space-y-1">
            <span className="text-zinc-500 text-xs font-mono uppercase tracking-wider block">Source Reference Path</span>
            <div className="bg-zinc-950/50 border border-zinc-900/60 p-3 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-2 font-mono text-zinc-400 text-xs">
                <Code className="h-4 w-4 text-indigo-400" />
                {spec.source}
              </div>
              <span className="text-[10px] text-zinc-500 uppercase font-mono">Verified perimeter file</span>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-zinc-900/60 flex flex-wrap justify-between items-center gap-4">
          <span className="text-xs text-zinc-500 font-mono">RFC context: {spec.rfc}</span>
          <div className="flex gap-2">
            <button onClick={() => triggerDownload("json")} className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 text-xs rounded-lg font-mono">
              JSON
            </button>
            <button onClick={() => triggerDownload("yaml")} className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 text-xs rounded-lg font-mono">
              YAML
            </button>
            <button onClick={() => triggerDownload("md")} className="px-3 py-1.5 bg-indigo-600 text-white hover:bg-indigo-700 text-xs rounded-lg font-mono">
              Markdown (.md)
            </button>
          </div>
        </div>
      </GlassCard>

    </div>
  );
}
