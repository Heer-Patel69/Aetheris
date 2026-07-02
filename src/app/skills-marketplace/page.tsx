"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, Compass, Download, Clock, DollarSign } from "lucide-react";
import { skills } from "@/data/skills";
import { GlassCard, GlowingBadge, SectionHeader } from "@/components/ui-components";

export default function SkillsMarketplace() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCat, setSelectedCat] = useState("All");

  const categories = ["All", "Intelligence", "Planning", "Database", "Frontend", "Backend", "DevOps", "Security", "Spatial", "Testing", "Analytics", "AI"];

  const filteredSkills = skills.filter((sk) => {
    const matchesSearch = 
      sk.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sk.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCat === "All" || sk.category === selectedCat;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="min-h-screen py-16 px-6 md:px-12 max-w-7xl mx-auto space-y-12">
      
      <SectionHeader 
        title="Specialist Skills Marketplace" 
        subtitle="Discover, inspect, and load verified agentic skills directly into your local Aetheris execution loops."
        badge="Skills Marketplace"
      />

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        {/* Search */}
        <div className="md:col-span-4 relative">
          <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-zinc-600" />
          <input
            type="text"
            placeholder="Search skills (e.g. optimizer)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-zinc-950/60 border border-zinc-900/60 rounded-xl py-3 pl-10 pr-4 text-xs focus:outline-none focus:border-indigo-500/80 transition-all font-mono"
          />
        </div>

        {/* Category Filters */}
        <div className="md:col-span-8 flex flex-wrap gap-1.5 justify-start md:justify-end">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCat(cat)}
              className={`px-3 py-1.5 rounded-lg text-[10px] font-semibold border transition-all \${
                selectedCat === cat
                  ? "bg-indigo-600/10 border-indigo-500/30 text-indigo-400"
                  : "bg-zinc-950/20 border-zinc-900/40 text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {filteredSkills.slice(0, 24).map((sk) => (
          <GlassCard key={sk.id} className="flex flex-col justify-between h-full p-6 space-y-6">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <GlowingBadge label={sk.category} variant="info" />
                <span className="text-[10px] text-zinc-600 font-mono">v{sk.version}</span>
              </div>
              <h3 className="text-sm font-bold text-zinc-200 leading-tight">{sk.name}</h3>
              <p className="text-zinc-500 text-[11px] leading-relaxed line-clamp-3">{sk.description}</p>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-2 bg-zinc-950/40 border border-zinc-900/60 p-2.5 rounded-lg text-center text-[10px] font-mono text-zinc-400">
                <div>
                  <span className="text-[8px] text-zinc-600 uppercase block">Latency</span>
                  {sk.latency}
                </div>
                <div>
                  <span className="text-[8px] text-zinc-600 uppercase block">Cost</span>
                  {sk.cost}
                </div>
                <div>
                  <span className="text-[8px] text-zinc-600 uppercase block">Score</span>
                  <span className="text-emerald-400">{sk.score}</span>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2 border-t border-zinc-900/40">
                <span className="text-[9px] text-zinc-500 font-mono uppercase">{sk.difficulty}</span>
                <Link
                  href={`/skills/\${sk.id}`}
                  className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-[10px] font-semibold flex items-center gap-1.5 transition-all"
                >
                  <Download className="h-3.5 w-3.5" />
                  View Skill
                </Link>
              </div>
            </div>
          </GlassCard>
        ))}
      </div>

    </div>
  );
}
