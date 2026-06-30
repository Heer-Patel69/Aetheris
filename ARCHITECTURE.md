# Aetheris Kernel — Architecture

**Version**: 3.0.0

---

## System Overview

Aetheris Kernel is an Autonomous Software Engineering Operating System (ASE-OS). It is structured into **8 core engines** that cooperate to automatically discover business requirements, make and record technology decisions, compile context packages, run concurrent task DAGs, handle autonomous build/compile recoveries, and enforce a strict Definition of Done (DoD) before completion.

## System Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                          AETHERIS KERNEL                               │
│  DAG Scheduler, worker pool execution, autonomous recovery engine      │
├───────────────────┬────────────────────┬───────────────────────────────┤
│  PRODUCT & ARCH   │  RUNTIME & CONTEXT │  STANDARDS &                  │
│  INTELLIGENCE     │  INTELLIGENCE      │  READINESS (ESRE)             │
│  ├ Product Disc.  │  ├ Incremental Scan│  ├ Standards Auditor          │
│  ├ Requirements   │  ├ Semantic Graph  │  └ DoD Readiness Check        │
│  ├ Architecture   │  ├ Resource Manager│                               │
│  └ Tech Decisions │  └ Local Enhancer  │                               │
├───────────────────┴────────────────────┴───────────────────────────────┤
│  MEMORY, KNOWLEDGE & LEARNING (MKLE)                                   │
│  ├ Project Memory  ├ Engineering Knowledge  ├ Workflow Memory  ├ Benchmarks│
├────────────────────────────────────────┬───────────────────────────────┤
│  ADAPTIVE ORCHESTRATION (AOL)          │  UNIVERSAL ADAPTER (UAL)      │
│  ├ Skill Router  └ Model Orchestrator  │  ├ IDE Adapter  └Model Adapter│
└────────────────────────────────────────┴───────────────────────────────┘
```

## Execution Pipeline

Aetheris does not run static linear phases. It compiles goals into dynamic Directed Acyclic Graphs (DAGs) and runs them concurrently:

```
Goal → Product Discovery → Architecture Design → DAG Build → Execute DAG ─► ESRE Audit ─► DoD Approved
                                                                ▲             │
                                                                └─ RCA & Fix ─┘
```

## Core Subsystems & Responsibilities

| Subsystem | Owner | Primary Purpose |
|---|---|---|
| Aetheris Kernel | Core Engine | Lifecycle management, concurrent task DAG scheduling, autonomous recovery rollbacks |
| PAIE | Product & Architecture | Product Discovery Loop (uncertainty mapping), requirements generation, technology decisions |
| RCIE | Runtime & Context | Incremental scanning, semantic graph relationships, resource management, local model enhancement |
| ESRE | Standards & Readiness | Enforce coding principles (SOLID, OWASP, Clean), WCAG accessibility audits, verify DoD |
| MKLE | Memory & Knowledge | Persistent storage for project config, reusable engineering patterns, execution history |
| AOL | Adaptive Orchestration | Dynamic registry scanner, versioning, routing of skills and LLM provider queries |
| UAL | Universal Adapter | Abstract IDE platforms (Cursor, Antigravity, CLI) and model endpoint clients |

## State Ownership Map

| State | Owner | Location |
|---|---|---|
| Global core config | Config Manager | `~/.aetheris/config/aetheris.yaml` |
| Project profiles & memory | MKLE | `<workspace>/.aetheris/memory/project-profile.yaml` |
| Architectural decisions | MKLE | `<workspace>/.aetheris/memory/decisions.jsonl` |
| Technology trade-off logs | PAIE / MKLE | `<workspace>/.aetheris/memory/tech-decisions.jsonl` |
| Reusable engineering patterns | MKLE | `~/.aetheris/knowledge/` |
| Telemetry & runtime benchmarks | MKLE | `~/.aetheris/benchmarks/` |

## Component-to-Implementation Mapping

| Engine | Namespace (under `src/`) | Entry points / Wrappers |
|---|---|---|
| Kernel | `kernel/` | `event_bus.py`, `telemetry.py`, `utils.py` |
| PAIE | `intelligence/` | `scanner.py`, `context.py` (wrappers) |
| RCIE | `intelligence/` | `scanner.py`, `context.py` (wrappers) |
| ESRE | `validation/` | `readiness.py` (readiness) |
| MKLE | `storage/` | `memory.py` (wrapper for storage manager) |
| AOL | `orchestration/` | `config.py`, `plugins.py`, `registry_cache.py`, `skill_scanner.py` |
| UAL | `adapters/` | `ide.py`, `model.py` |

## Configuration Hierarchy

```
Level 1 — aetheris/config/*.yaml (shipped defaults, lowest priority)
Level 2 — ~/.aetheris/config/*.yaml (user overrides)
Level 3 — <workspace>/.aetheris/config/*.yaml (project overrides)
Level 4 — Runtime overrides (highest priority, not persisted)
```

## Platform Constraints

| Constraint | Impact | Workaround |
|---|---|---|
| No programmatic model switching | LLM Router is advisory | Recommend model in trace; adapt to active model |
| No request interception | Aetheris Kernel activation not guaranteed | Global AGENTS.md as fallback instruction |
| No token count access | Cost optimization is estimation-based | Advisory cost tracking, not metering |
| No background processes | No persistent daemon | Scripts invoked on-demand; state persists via filesystem |