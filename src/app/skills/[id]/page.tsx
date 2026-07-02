"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Download } from "lucide-react";
import { skills } from "@/data/skills";
import { GlassCard, GlowingBadge } from "@/components/ui-components";

export default function SkillDetailPage() {
  const { id } = useParams();
  const skill = skills.find((s) => s.id === id) || skills[0];

  const triggerDownload = (format: "yaml" | "json" | "md") => {
    let content = "";
    if (format === "yaml") {
      content = `---
name: \${skill.name}
version: \${skill.version}
description: \${skill.description}
difficulty: \${skill.difficulty}
latency_target: \${skill.latency}
cost_target: \${skill.cost}
...`;
    } else if (format === "json") {
      content = JSON.stringify(skill, null, 2);
    } else {
      content = `# Specialist Skill: \${skill.name}

## Description
\${skill.description}

## Parameters
- Version: \${skill.version}
- Difficulty: \${skill.difficulty}
- Target Latency: \${skill.latency}
- Estimated Cost: \${skill.cost}

## Inputs
\${skill.inputs}

## Outputs
\${skill.outputs}
`;
    }

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `\${skill.id}.\${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-4xl mx-auto space-y-8">
      
      <Link href="/skills-marketplace" className="inline-flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
        <ArrowLeft className="h-4 w-4" />
        Back to Marketplace
      </Link>

      <GlassCard hoverEffect={false} className="p-8 space-y-6">
        <div className="flex justify-between items-start border-b border-zinc-900/60 pb-6">
          <div className="space-y-1">
            <span className="text-indigo-400 text-xs font-mono font-bold">Specialist Skill Configuration</span>
            <h1 className="text-2xl md:text-3xl font-extrabold text-zinc-50">{skill.name}</h1>
          </div>
          <GlowingBadge label={skill.category} variant="info" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 text-sm">
          <div className="md:col-span-8 space-y-6">
            <div className="space-y-1">
              <span className="text-zinc-500 text-xs font-mono uppercase block">Description</span>
              <p className="text-zinc-300 leading-relaxed">{skill.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <span className="text-zinc-500 text-xs font-mono uppercase block">Inputs Protocol</span>
                <div className="bg-zinc-950/40 p-3 rounded-lg border border-zinc-900/60 font-mono text-xs text-zinc-400">
                  {skill.inputs}
                </div>
              </div>
              <div className="space-y-1">
                <span className="text-zinc-500 text-xs font-mono uppercase block">Outputs Protocol</span>
                <div className="bg-zinc-950/40 p-3 rounded-lg border border-zinc-900/60 font-mono text-xs text-zinc-400">
                  {skill.outputs}
                </div>
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-zinc-500 text-xs font-mono uppercase block">Required Models</span>
              <div className="flex gap-2 pt-1">
                {skill.requiredModels.map((m, idx) => (
                  <span key={idx} className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded text-xs font-mono">
                    {m}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="md:col-span-4 bg-zinc-950/30 border border-zinc-900/60 rounded-xl p-6 space-y-4 h-fit">
            <h3 className="text-xs font-bold text-zinc-300 border-b border-zinc-900 pb-2">Target Performance</h3>
            
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between">
                <span className="text-zinc-600">Difficulty</span>
                <span className="text-zinc-400">{skill.difficulty}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-600">Latency</span>
                <span className="text-zinc-400">{skill.latency}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-600">Target Cost</span>
                <span className="text-zinc-400">{skill.cost}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-600">Quality Index</span>
                <span className="text-emerald-400">{skill.score}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-zinc-900/60 flex flex-wrap justify-between items-center gap-4">
          <span className="text-xs text-zinc-500 font-mono">Compatible with Aetheris OS CLI</span>
          <div className="flex gap-2">
            <button onClick={() => triggerDownload("md")} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors">
              <Download className="h-4 w-4" />
              Download Markdown (.md)
            </button>
            <button onClick={() => triggerDownload("yaml")} className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-lg text-xs font-semibold transition-colors font-mono">
              YAML
            </button>
            <button onClick={() => triggerDownload("json")} className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-lg text-xs font-semibold transition-colors font-mono">
              JSON
            </button>
          </div>
        </div>
      </GlassCard>

    </div>
  );
}
