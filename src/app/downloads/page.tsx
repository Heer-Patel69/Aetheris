"use client";

import React, { useState } from "react";
import { Terminal as TerminalIcon, Copy, Check } from "lucide-react";
import { GlassCard, GlowingBadge, SectionHeader } from "@/components/ui-components";

export default function Downloads() {
  const [copiedText, setCopiedText] = useState("");

  const commands = {
    pip: "pip install aetheris",
    curl: "curl -fsSL https://aetheris.dev/install.sh | sh",
    docker: "docker run -it aetheris/kernel:latest --goal 'Init'",
  };

  const copyToClipboard = (key: keyof typeof commands) => {
    navigator.clipboard.writeText(commands[key]);
    setCopiedText(key);
    setTimeout(() => setCopiedText(""), 2000);
  };

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-4xl mx-auto space-y-12">
      
      <SectionHeader 
        title="Installation Center" 
        subtitle="Install the Aetheris CLI execution tools on your local host system."
        badge="CLI Download"
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* PIP */}
        <GlassCard hoverEffect={false} className="space-y-4">
          <div className="flex justify-between items-center">
            <GlowingBadge label="Python PIP" variant="info" />
            <button onClick={() => copyToClipboard("pip")} className="text-zinc-500 hover:text-zinc-300">
              {copiedText === "pip" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
            </button>
          </div>
          <h3 className="text-sm font-bold text-zinc-200">Local package</h3>
          <p className="text-zinc-500 text-xs">Run inside your local virtual environment.</p>
          <pre className="bg-zinc-950 p-3 rounded-lg font-mono text-[10px] text-zinc-300 overflow-x-auto">
            {commands.pip}
          </pre>
        </GlassCard>

        {/* Curl */}
        <GlassCard hoverEffect={false} className="space-y-4">
          <div className="flex justify-between items-center">
            <GlowingBadge label="Bash shell" variant="info" />
            <button onClick={() => copyToClipboard("curl")} className="text-zinc-500 hover:text-zinc-300">
              {copiedText === "curl" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
            </button>
          </div>
          <h3 className="text-sm font-bold text-zinc-200">Unix Installer</h3>
          <p className="text-zinc-500 text-xs">Download and setup globally on Linux/macOS.</p>
          <pre className="bg-zinc-950 p-3 rounded-lg font-mono text-[10px] text-zinc-300 overflow-x-auto">
            {commands.curl}
          </pre>
        </GlassCard>

        {/* Docker */}
        <GlassCard hoverEffect={false} className="space-y-4">
          <div className="flex justify-between items-center">
            <GlowingBadge label="Docker Engine" variant="info" />
            <button onClick={() => copyToClipboard("docker")} className="text-zinc-500 hover:text-zinc-300">
              {copiedText === "docker" ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
            </button>
          </div>
          <h3 className="text-sm font-bold text-zinc-200">Container sandbox</h3>
          <p className="text-zinc-500 text-xs">Run completely containerized, no host dependencies.</p>
          <pre className="bg-zinc-950 p-3 rounded-lg font-mono text-[10px] text-zinc-300 overflow-x-auto">
            {commands.docker}
          </pre>
        </GlassCard>

      </div>

    </div>
  );
}
