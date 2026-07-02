"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Cpu, Search, HelpCircle, FileText, Database, Compass, Terminal, Menu, X } from "lucide-react";
import { GlowingBadge } from "./ui-components";
import CommandPalette from "./command-palette";

export default function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);

  const navItems = [
    { name: "Story", href: "/what-is-aetheris", icon: HelpCircle },
    { name: "RFCs", href: "/rfc-explorer", icon: FileText },
    { name: "SPECs", href: "/spec-explorer", icon: Database },
    { name: "Skills", href: "/skills-marketplace", icon: Compass },
    { name: "Playground", href: "/playground", icon: Cpu },
    { name: "Docs", href: "/docs", icon: FileText },
    { name: "Dashboard", href: "/dashboard", icon: Terminal },
    { name: "Install", href: "/downloads", icon: Terminal }
  ];

  return (
    <nav className="glass-nav sticky top-0 left-0 right-0 z-50 w-full px-6 py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/25">
            <Cpu className="h-5 w-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg tracking-tight uppercase text-zinc-100">
              AETHERIS
            </span>
            <span className="text-[10px] text-zinc-500 font-mono tracking-wider">
              AI ENGINE OS
            </span>
          </div>
        </Link>

        {/* Navigation Items (Desktop) */}
        <div className="hidden lg:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all \${
                  isActive
                    ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/20"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40 border border-transparent"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {item.name}
              </Link>
            );
          })}
        </div>

        {/* Action Panel */}
        <div className="flex items-center gap-3">
          {/* Global Cmd+K Search trigger */}
          <button
            onClick={() => setPaletteOpen(true)}
            className="flex items-center gap-2 bg-zinc-950/80 border border-zinc-900/60 rounded-lg px-3 py-1.5 text-zinc-400 hover:text-zinc-200 text-xs font-mono transition-all"
          >
            <Search className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Search</span>
            <kbd className="hidden md:inline bg-zinc-900 border border-zinc-800 px-1 py-0.5 rounded text-[10px]">⌘K</kbd>
          </button>
          
          <GlowingBadge label="Kernel Live" variant="success" className="hidden sm:inline-flex" />

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-zinc-400 hover:text-zinc-200"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

      </div>

      {/* Mobile Menu Panel */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-zinc-900/60 bg-zinc-950/95 backdrop-blur-xl absolute top-full left-0 right-0 p-6 flex flex-col gap-3 shadow-2xl">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-3 px-4 py-3 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/60 text-sm font-semibold"
              >
                <Icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
        </div>
      )}

      {/* Command Palette search portal */}
      {paletteOpen && <CommandPalette onClose={() => setPaletteOpen(false)} />}
    </nav>
  );
}
