"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { docs } from "@/data/docs";
import { GlassCard } from "@/components/ui-components";

export default function DocDetailPage() {
  const { slug } = useParams();
  const currentSlug = Array.isArray(slug) ? slug[0] : slug;
  const doc = docs.find((d) => d.slug === currentSlug) || docs[0];

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-4xl mx-auto space-y-8">
      
      <Link href="/docs" className="inline-flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
        <ArrowLeft className="h-4 w-4" />
        Back to Portal
      </Link>

      <GlassCard hoverEffect={false} className="p-8 space-y-6">
        <div className="prose prose-invert max-w-none text-zinc-300 text-sm leading-relaxed space-y-4">
          <div className="border-b border-zinc-900/60 pb-4 mb-6">
            <span className="text-indigo-400 font-mono text-xs font-bold uppercase">{doc.category}</span>
            <h1 className="text-2xl md:text-3xl font-extrabold text-zinc-50 mt-1">{doc.title}</h1>
          </div>
          
          {doc.content.split("\n\n").map((block, idx) => {
            const line = block.trim();
            if (line.startsWith("# ")) return null;
            if (line.startsWith("## ")) {
              return <h3 key={idx} className="text-lg font-bold text-zinc-200 pt-4">{line.replace("## ", "")}</h3>;
            }
            if (line.startsWith("### ")) {
              return <h4 key={idx} className="text-sm font-bold text-zinc-300 pt-2">{line.replace("### ", "")}</h4>;
            }
            if (line.startsWith("\`\`\`")) {
              const code = line.replace(/\`\`\`[a-z]*/g, "").replace(/\`\`\`/g, "").trim();
              return (
                <pre key={idx} className="bg-zinc-950 border border-zinc-900 p-4 rounded-lg font-mono text-xs text-zinc-300 overflow-x-auto whitespace-pre">
                  {code}
                </pre>
              );
            }
            return <p key={idx} className="text-zinc-400">{line}</p>;
          })}
        </div>
      </GlassCard>

    </div>
  );
}
