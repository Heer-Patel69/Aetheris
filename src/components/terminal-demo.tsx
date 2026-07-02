"use client";

import React, { useState, useEffect } from "react";
import { Terminal as TerminalIcon, RefreshCw } from "lucide-react";
import { GlassCard, TerminalRow } from "./ui-components";

export default function TerminalDemo() {
  const [terminalStep, setTerminalStep] = useState(0);

  const logs = [
    { label: "INIT", val: "Initializing Aetheris Kernel v3.1...", stat: "normal" as const },
    { label: "WDE", val: "Scanning repository structures: Next.js + Tailwind CSS verified.", stat: "normal" as const },
    { label: "URUE", val: "Ingesting intent target: 'Build OAuth validation flow'", stat: "normal" as const },
    { label: "PDE", val: "Decomposing objectives into feature plan roadmap...", stat: "success" as const },
    { label: "APE", val: "Compiling system domain schema blueprint", stat: "success" as const },
    { label: "SIS", dec: "Selecting specialist: 'agency-backend-architect'", stat: "success" as const },
    { label: "EXEC", val: "Executing task: generate oauth_controller.py", stat: "pending" as const },
    { label: "VERIFY", val: "Running DoD audit: quality check passed (98%)", stat: "success" as const },
    { label: "DONE", val: "Successfully merged changes to main.", stat: "success" as const }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setTerminalStep((prev) => (prev < logs.length ? prev + 1 : 0));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <GlassCard hoverEffect={false} className="font-mono bg-zinc-950/80 border border-zinc-800/80 p-0 overflow-hidden shadow-2xl">
      <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-rose-500/80" />
          <div className="w-3 h-3 rounded-full bg-amber-500/80" />
          <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
        </div>
        <div className="flex items-center gap-1.5 text-xs text-zinc-500 font-mono">
          <TerminalIcon className="h-3.5 w-3.5" />
          aetheris_sandbox_terminal.sh
        </div>
        <div className="w-12" />
      </div>

      <div className="p-4 h-[280px] overflow-y-auto flex flex-col gap-1 select-none text-xs">
        <div className="text-zinc-500 mb-2">$ aetheris --goal &quot;Build OAuth validation flow&quot;</div>
        {logs.slice(0, terminalStep).map((log, index) => (
          <TerminalRow 
            key={index}
            label={`[\${log.label}]`} 
            value={log.val || log.dec || ""} 
            status={log.stat} 
          />
        ))}
        {terminalStep < logs.length && (
          <div className="text-indigo-400 font-semibold animate-pulse mt-1.5 flex items-center gap-2">
            <RefreshCw className="h-3 w-3 animate-spin" />
            Executing Kernel DAG...
          </div>
        )}
      </div>
    </GlassCard>
  );
}
