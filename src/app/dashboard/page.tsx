"use client";

import React, { useState, useEffect } from "react";
import { Cpu, Zap, Activity, Clock, ShieldCheck } from "lucide-react";
import { GlassCard, GlowingBadge, TerminalRow } from "@/components/ui-components";

export default function Dashboard() {
  const [logs, setLogs] = useState<Array<{ time: string; event: string; status: "success" | "pending" | "normal" }>>([
    { time: "01:15:32", event: "Workspace scanner scans main.py: OK.", status: "success" },
    { time: "01:15:35", event: "Model routed to gemini-2.5-flash for token budget optimization.", status: "normal" },
    { time: "01:15:38", event: "ACGE file changes generated.", status: "success" },
  ]);

  useEffect(() => {
    const events = [
      "Running DoD validation on src/components/navbar.tsx...",
      "Self review engine approved changes (98%).",
      "Model routing request dispatched for SPEC-039.",
      "Experience memory engine: recorded 12ms latency reduction.",
      "Self evolution orchestrator triggered source file scan.",
    ];

    const interval = setInterval(() => {
      const time = new Date().toTimeString().split(" ")[0];
      const randomEvent = events[Math.floor(Math.random() * events.length)];
      setLogs((prev) => [
        { time, event: randomEvent, status: "normal" as const },
        ...prev.slice(0, 4),
      ]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-7xl mx-auto space-y-12">
      
      <div className="text-center md:text-left space-y-2">
        <GlowingBadge label="Telemetry Console" variant="success" />
        <h1 className="text-3xl font-extrabold text-zinc-50">System Performance & Telemetry</h1>
        <p className="text-zinc-400 text-xs max-w-md">
          Continuous latency tracking, cost estimation profiles, and live audit trailing.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="flex items-center gap-4">
          <div className="p-3.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <Clock className="h-6 w-6" />
          </div>
          <div>
            <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider block">Average Latency</span>
            <span className="text-lg font-bold text-zinc-100 font-mono">1.84 seconds</span>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-3.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider block">Total Sessions Run</span>
            <span className="text-lg font-bold text-zinc-100 font-mono">241,192 runs</span>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-3.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider block">Health Score</span>
            <span className="text-lg font-bold text-emerald-400 font-mono">99.85% Compliant</span>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Latency Chart */}
        <div className="lg:col-span-8">
          <GlassCard hoverEffect={false} className="space-y-6">
            <div className="flex justify-between items-center border-b border-zinc-900/60 pb-4">
              <span className="text-xs font-bold text-zinc-300">Model Latency Profile (Seconds)</span>
              <GlowingBadge label="Real-time check" variant="info" />
            </div>

            <div className="w-full flex justify-center">
              <svg className="w-full max-w-lg h-44" viewBox="0 0 400 150">
                <line x1="40" y1="20" x2="380" y2="20" stroke="#1f1f23" strokeDasharray="3,3" />
                <line x1="40" y1="60" x2="380" y2="60" stroke="#1f1f23" strokeDasharray="3,3" />
                <line x1="40" y1="100" x2="380" y2="100" stroke="#1f1f23" strokeDasharray="3,3" />
                <line x1="40" y1="130" x2="380" y2="130" stroke="#27272a" />

                {/* Gemini 2.5 Flash */}
                <rect x="60" y="110" width="30" height="20" fill="#6366f1" rx="4" />
                <text x="75" y="142" fill="#52525b" fontSize="8" textAnchor="middle" fontFamily="monospace">Gemini Flash</text>
                <text x="75" y="102" fill="#6366f1" fontSize="8" textAnchor="middle" fontFamily="monospace">1.1s</text>

                {/* GPT-4o */}
                <rect x="150" y="80" width="30" height="50" fill="#6366f1" rx="4" />
                <text x="165" y="142" fill="#52525b" fontSize="8" textAnchor="middle" fontFamily="monospace">GPT-4o</text>
                <text x="165" y="72" fill="#6366f1" fontSize="8" textAnchor="middle" fontFamily="monospace">2.1s</text>

                {/* Claude Sonnet */}
                <rect x="240" y="75" width="30" height="55" fill="#6366f1" rx="4" />
                <text x="255" y="142" fill="#52525b" fontSize="8" textAnchor="middle" fontFamily="monospace">Claude 3.5</text>
                <text x="255" y="67" fill="#6366f1" fontSize="8" textAnchor="middle" fontFamily="monospace">2.3s</text>

                {/* Gemini Pro */}
                <rect x="330" y="40" width="30" height="90" fill="#818cf8" rx="4" />
                <text x="345" y="142" fill="#52525b" fontSize="8" textAnchor="middle" fontFamily="monospace">Gemini Pro</text>
                <text x="345" y="32" fill="#818cf8" fontSize="8" textAnchor="middle" fontFamily="monospace">4.5s</text>
              </svg>
            </div>
          </GlassCard>
        </div>

        {/* Live Logs */}
        <div className="lg:col-span-4">
          <GlassCard hoverEffect={false} className="space-y-4 font-mono h-full flex flex-col justify-between p-6">
            <div className="space-y-1 pb-3 border-b border-zinc-900/60">
              <span className="text-indigo-400 text-[9px] font-bold">MONITOR</span>
              <h3 className="text-xs font-bold text-zinc-300">Live Kernel Journal</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto space-y-2 py-4 h-[180px]">
              {logs.map((log, idx) => (
                <TerminalRow
                  key={idx}
                  label={log.time}
                  value={log.event}
                  status={log.status}
                />
              ))}
            </div>
          </GlassCard>
        </div>
      </div>

    </div>
  );
}
