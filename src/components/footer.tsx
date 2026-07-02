"use client";

import React from "react";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-zinc-900/60 bg-zinc-950/20 py-16 px-6 mt-auto">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        
        <div className="space-y-3">
          <span className="text-sm font-bold tracking-wider uppercase text-zinc-300">AETHERIS PLATFORM</span>
          <p className="text-xs text-zinc-500 leading-relaxed max-w-xs">
            Autonomous software engineering operating system driven by specifications, RFC guidelines, and modular pipeline schedules.
          </p>
        </div>

        <div className="space-y-3 text-xs">
          <span className="font-semibold text-zinc-400">Explore</span>
          <div className="flex flex-col gap-2 text-zinc-500">
            <Link href="/rfc-explorer" className="hover:text-zinc-300">Subsystem RFCs</Link>
            <Link href="/spec-explorer" className="hover:text-zinc-300">Implementation SPECs</Link>
            <Link href="/skills-marketplace" className="hover:text-zinc-300">Skills Marketplace</Link>
          </div>
        </div>

        <div className="space-y-3 text-xs">
          <span className="font-semibold text-zinc-400">Resources</span>
          <div className="flex flex-col gap-2 text-zinc-500">
            <Link href="/docs" className="hover:text-zinc-300">Installation Docs</Link>
            <Link href="/playground" className="hover:text-zinc-300">AI Playground</Link>
            <Link href="/dashboard" className="hover:text-zinc-300">Telemetry Console</Link>
          </div>
        </div>

        <div className="space-y-3 text-xs">
          <span className="font-semibold text-zinc-400">Community</span>
          <div className="flex flex-col gap-2 text-zinc-500">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-zinc-300">GitHub Docs</a>
            <a href="https://discord.com" target="_blank" rel="noreferrer" className="hover:text-zinc-300">Discord OS</a>
          </div>
        </div>

      </div>
      <div className="max-w-7xl mx-auto text-center md:text-left mt-12 pt-8 border-t border-zinc-900/40">
        <span className="text-[10px] text-zinc-600 font-mono">
          &copy; {new Date().getFullYear()} Aetheris Platform. Compliant under standard ISO guidelines. All rights reserved.
        </span>
      </div>
    </footer>
  );
}
