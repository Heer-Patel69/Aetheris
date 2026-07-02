"use client";

import React, { useState } from "react";
import { Cpu, RefreshCw } from "lucide-react";
import { GlassCard, GlowingBadge, SectionHeader, TerminalRow } from "@/components/ui-components";

export default function Playground() {
  const [goal, setGoal] = useState("");
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);

  const triggerMockRun = () => {
    if (!goal.trim()) return;
    setRunning(true);
    setSuccess(false);
    setStep([]);

    const pipeline = [
      "WDE: Workspace walker indexed 18 files.",
      "URUE: Requirement understanding converted intent to specifications.",
      "PDE: Generated product requirements with compliance constraints.",
      "APE: Designed PostgreSQL database schema model.",
      "SIS: Assigned DeveloperAgent to generate controllers.",
      "ACGE: Successfully edited 2 workspace files.",
      "DoD Auditor: Code verification score 100% compliant."
    ];

    pipeline.forEach((msg, idx) => {
      setTimeout(() => {
        setStep((prev) => [...prev, msg]);
        if (idx === pipeline.length - 1) {
          setRunning(false);
          setSuccess(true);
        }
      }, (idx + 1) * 1200);
    });
  };

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-4xl mx-auto space-y-12">
      
      <SectionHeader 
        title="Interactive Playground" 
        subtitle="Simulate the Aetheris Kernel compilation loop in real-time."
        badge="Engine Simulation"
      />

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        <div className="md:col-span-5 space-y-4">
          <GlassCard hoverEffect={false} className="space-y-4">
            <div className="space-y-2">
              <span className="text-zinc-500 font-mono text-[10px] uppercase">Goal Definition</span>
              <textarea
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="e.g. Build an API endpoint with Redis cache middleware"
                disabled={running}
                className="w-full h-32 bg-zinc-950/60 border border-zinc-900/60 rounded-xl p-3 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500/80 resize-none"
              />
            </div>

            <button
              onClick={triggerMockRun}
              disabled={running || !goal.trim()}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-zinc-900 disabled:text-zinc-700 text-white rounded-xl text-xs font-bold transition-colors flex items-center justify-center gap-2"
            >
              {running ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Cpu className="h-4 w-4" />}
              {running ? "Compiling DAG..." : "Execute Goal"}
            </button>
          </GlassCard>
        </div>

        <div className="md:col-span-7">
          <GlassCard hoverEffect={false} className="font-mono bg-zinc-950 p-6 border border-zinc-800/80 h-full flex flex-col justify-between">
            <div className="space-y-3">
              <div className="border-b border-zinc-900/60 pb-3 flex justify-between items-center">
                <span className="text-xs font-bold text-zinc-300">Live Console Output</span>
                {success && <GlowingBadge label="DoD Verified" variant="success" />}
              </div>

              <div className="space-y-2 text-[10px] select-none text-zinc-400">
                {step.map((msg, idx) => (
                  <div key={idx} className="flex gap-2 items-start py-0.5 border-b border-zinc-900/40">
                    <span className="text-indigo-400 font-bold flex-shrink-0">&gt;</span>
                    <span>{msg}</span>
                  </div>
                ))}
              </div>
            </div>

            {running && (
              <div className="text-[10px] text-zinc-500 animate-pulse mt-4 flex items-center gap-2">
                <RefreshCw className="h-3 w-3 animate-spin text-indigo-400" />
                Kernel orchestrating active engines...
              </div>
            )}
          </GlassCard>
        </div>
      </div>

    </div>
  );
}
