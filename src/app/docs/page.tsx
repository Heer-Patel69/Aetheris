"use client";

import React from "react";
import Link from "next/link";
import { docs } from "@/data/docs";
import { GlassCard, GlowingBadge, SectionHeader } from "@/components/ui-components";

export default function DocsPortal() {
  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-5xl mx-auto space-y-12">
      
      <SectionHeader 
        title="Documentation Portal" 
        subtitle="Access manuals, reference definitions, operational guidelines, and CLI details."
        badge="Engineering Docs"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {docs.map((doc) => (
          <GlassCard key={doc.slug} className="flex flex-col justify-between h-full space-y-4">
            <div className="space-y-2">
              <GlowingBadge label={doc.category} variant="info" />
              <h3 className="text-lg font-bold text-zinc-200">{doc.title}</h3>
              <p className="text-zinc-500 text-xs leading-relaxed line-clamp-3">
                {doc.content.replace(/[#*`]/g, "").substring(0, 150)}...
              </p>
            </div>
            
            <div className="pt-2">
              <Link 
                href={`/docs/\${doc.slug}`}
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                Read Article
              </Link>
            </div>
          </GlassCard>
        ))}
      </div>

    </div>
  );
}
