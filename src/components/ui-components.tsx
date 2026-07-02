"use client";

import React from "react";
import { motion, HTMLMotionProps } from "framer-motion";

interface GlassCardProps extends HTMLMotionProps<"div"> {
  hoverEffect?: boolean;
}

export function GlassCard({ children, hoverEffect = true, className = "", ...props }: GlassCardProps) {
  return (
    <motion.div
      whileHover={hoverEffect ? { y: -4, borderColor: "rgba(99, 102, 241, 0.45)", boxShadow: "0 10px 40px -10px rgba(99, 102, 241, 0.25)" } : {}}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`glass-panel p-6 \${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
}

interface GlowingBadgeProps {
  label: string;
  variant?: "success" | "info" | "warning" | "error";
  className?: string;
}

export function GlowingBadge({ label, variant = "info", className = "" }: GlowingBadgeProps) {
  const colors = {
    success: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/30", ping: "bg-emerald-500" },
    info: { bg: "bg-indigo-500/10", text: "text-indigo-400", border: "border-indigo-500/30", ping: "bg-indigo-500" },
    warning: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/30", ping: "bg-amber-500" },
    error: { bg: "bg-rose-500/10", text: "text-rose-400", border: "border-rose-500/30", ping: "bg-rose-500" },
  };

  const selected = colors[variant];

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full border \${selected.bg} \${selected.text} \${selected.border} \${className}`}>
      <span className="relative flex h-2 w-2">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 \${selected.ping}`}></span>
        <span className={`relative inline-flex rounded-full h-2 w-2 \${selected.ping}`}></span>
      </span>
      {label}
    </div>
  );
}

interface TerminalRowProps {
  label: string;
  value: string;
  status?: "success" | "pending" | "normal";
}

export function TerminalRow({ label, value, status = "normal" }: TerminalRowProps) {
  const statusColors = {
    success: "text-emerald-400 font-semibold",
    pending: "text-amber-400 animate-pulse",
    normal: "text-zinc-300",
  };

  return (
    <div className="flex items-center justify-between py-1.5 border-b border-zinc-900/60 text-xs font-mono">
      <span className="text-zinc-500">{label}</span>
      <span className={statusColors[status]}>{value}</span>
    </div>
  );
}

export function SectionHeader({ title, subtitle, badge }: { title: string; subtitle?: string; badge?: string }) {
  return (
    <div className="space-y-2">
      {badge && <GlowingBadge label={badge} variant="info" />}
      <h2 className="text-2xl md:text-4xl font-extrabold tracking-tight text-zinc-50">{title}</h2>
      {subtitle && <p className="text-zinc-400 text-sm max-w-2xl">{subtitle}</p>}
    </div>
  );
}

export function StatCard({ value, label, icon: Icon }: { value: string; label: string; icon?: React.ComponentType<any> }) {
  return (
    <GlassCard className="text-center py-8">
      {Icon && <div className="flex justify-center text-indigo-400 mb-3"><Icon className="h-6 w-6" /></div>}
      <div className="text-2xl md:text-3xl font-extrabold text-zinc-50 font-mono">{value}</div>
      <div className="text-[10px] text-zinc-500 mt-1 uppercase tracking-wider">{label}</div>
    </GlassCard>
  );
}
