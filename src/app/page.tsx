"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Cpu, ShieldCheck, Database, Award, Zap } from "lucide-react";
import TerminalDemo from "@/components/terminal-demo";
import HeroScene from "@/components/hero-scene";
import { GlassCard, GlowingBadge, StatCard } from "@/components/ui-components";

export default function Home() {
  return (
    <div className="min-h-screen relative flex flex-col justify-between py-12 px-6 md:px-12 max-w-7xl mx-auto space-y-24">
      
      {/* Premium R3F starfield scene */}
      <HeroScene />

      {/* Hero Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center pt-12">
        <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
          <GlowingBadge label="Aetheris Platform Live" variant="info" />
          
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-none bg-gradient-to-r from-zinc-50 via-zinc-200 to-indigo-400 bg-clip-text text-transparent">
            The Autonomous OS for AI Software Engineering.
          </h1>

          <p className="text-zinc-400 text-base md:text-lg leading-relaxed max-w-xl mx-auto lg:mx-0">
            Aetheris is an autonomous, specification-driven operating system designed to convert high-level objectives into production-ready software repositories.
          </p>

          <div className="flex flex-wrap gap-4 justify-center lg:justify-start pt-2">
            <Link
              href="/docs"
              className="px-6 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-lg shadow-indigo-600/25 flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              Get Started
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/playground"
              className="px-6 py-3.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 hover:text-white rounded-xl text-xs font-bold flex items-center gap-2 transition-all"
            >
              Try Playground
            </Link>
          </div>
        </div>

        {/* Animated Terminal Simulator */}
        <div className="lg:col-span-5">
          <TerminalDemo />
        </div>
      </div>

      {/* Deep Story/Philosophy Section */}
      <div className="space-y-12">
        <div className="text-center space-y-3">
          <GlowingBadge label="Platform Vision" variant="success" />
          <h2 className="text-3xl font-extrabold text-zinc-150">The Evolution of AI Coding</h2>
          <p className="text-zinc-500 text-sm max-w-lg mx-auto">
            Why autocomplete widgets and conversational wrappers fail to scale on enterprise codebases.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-xs leading-relaxed">
          <GlassCard className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-200">1. Autonomous vs Assistant</h3>
            <p className="text-zinc-400">
              Legacy assistants require constant micro-management, prompting, and copy-pasting. Aetheris operates asynchronously, parsing entire workspaces, planning dependency charts, writing logic, compiling targets, and self-repairing build errors before delivering the final code package.
            </p>
          </GlassCard>

          <GlassCard className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-200">2. Specification Rules</h3>
            <p className="text-zinc-400">
              Unstructured edits create cyclic reference loops and broken builds. Aetheris binds its execution engines to precise SPEC definitions and RFC standards, guaranteeing modular correctness and clean architecture.
            </p>
          </GlassCard>
        </div>
      </div>

      {/* Telemetry Dashboard Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <StatCard value="10 RFCs" label="Operating Architecture" icon={Database} />
        <StatCard value="170 SPECs" label="Engine Specifications" icon={Cpu} />
        <StatCard value="244 Skills" label="Specialist Agents" icon={Zap} />
        <StatCard value="100% Audit" label="Quality Compliance" icon={Award} />
      </div>

    </div>
  );
}
