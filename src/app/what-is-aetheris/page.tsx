"use client";

import React from "react";
import { Cpu, ShieldCheck, Database, Award, BookOpen, Clock } from "lucide-react";
import { GlassCard, GlowingBadge, SectionHeader } from "@/components/ui-components";

export default function WhatIsAetheris() {
  const subsystems = [
    { name: "EKS", desc: "Engineering Knowledge System - Traverses directories and compiles code dependency graphs." },
    { name: "RUS", desc: "Requirement Understanding System - Ingests prompt intentions and analyzes limitations." },
    { name: "PPS", desc: "Product Planning System - Generates timelines, personae grids, and functional requirements." },
    { name: "APS", desc: "Architecture Planning System - Models domain layer dividers and database schemas." },
    { name: "SIS", desc: "Skill Intelligence System - Matches developer specialization profiles with task DAG items." },
    { name: "MIS", desc: "Model Intelligence System - Routes active tasks to cost-optimized LLM nodes." },
    { name: "AES", desc: "Autonomous Execution System - Executes shell scripts, saves code revisions, and commits git modifications." },
    { name: "VQS", desc: "Verification & Quality System - Conducts WCAG audits, security validation, and unit tests." }
  ];

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-5xl mx-auto space-y-16">
      
      <SectionHeader 
        title="What is Aetheris?" 
        subtitle="Exploring the modular design principles and core specifications driving the autonomous operating system."
        badge="Platform Mission"
      />

      <div className="space-y-6 text-sm text-zinc-400 leading-relaxed">
        <h2 className="text-lg font-bold text-zinc-150">Origin & Development Roadmap</h2>
        <p>
          Aetheris was conceptualized in early 2025 to solve the limitations of standard generative AI coding. Traditional systems lack context memory, write invalid imports, and fail during complex dependency refactoring.
        </p>
        <p>
          By framing AI software engineering as a dynamic scheduling problem on topological graphs, Aetheris models tasks as nodes in a Directed Acyclic Graph (DAG). This approach separates logical planning from code edits, ensuring all edits conform to local rules.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <GlassCard className="space-y-3">
          <div className="flex items-center gap-3 text-indigo-400 font-bold">
            <Cpu className="h-5 w-5" />
            <h3>Autonomous Architecture</h3>
          </div>
          <p className="text-zinc-400 text-xs leading-relaxed">
            Unlike standard coding interfaces, Aetheris runs as a decoupled state pipeline loop. It compiles requirements into detailed topological dependency trees, preventing unstructured edits and random compilation failures.
          </p>
        </GlassCard>

        <GlassCard className="space-y-3">
          <div className="flex items-center gap-3 text-emerald-400 font-bold">
            <ShieldCheck className="h-5 w-5" />
            <h3>Quality Verification</h3>
          </div>
          <p className="text-zinc-400 text-xs leading-relaxed">
            Every file modification undergoes self-review, automated linting, and regression tests. The code generator is strictly containerized, preserving host machine security.
          </p>
        </GlassCard>
      </div>

      {/* Subsystems */}
      <div className="space-y-6">
        <SectionHeader title="The Core Subsystems" subtitle="A network of cooperative specialist modules coordinating execution." />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {subsystems.map((sub, idx) => (
            <div key={idx} className="bg-zinc-950/60 border border-zinc-900/60 p-4 rounded-xl flex items-start gap-4">
              <div className="h-9 w-9 rounded-lg bg-zinc-900 flex items-center justify-center font-mono font-bold text-xs text-indigo-400 border border-zinc-800 flex-shrink-0">
                {sub.name}
              </div>
              <div className="space-y-1">
                <span className="text-xs font-bold text-zinc-300">{sub.name} Subsystem</span>
                <p className="text-[11px] text-zinc-500 leading-normal">{sub.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
