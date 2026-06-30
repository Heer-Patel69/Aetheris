# UniVoid Brain OS — Architecture

**Version**: 2.0.0

---

## System Overview

UniVoid Brain OS is a modular AI orchestration runtime for Antigravity. It coordinates 217 specialized Agency agents through an 8-stage execution pipeline, deployed as a combination of Antigravity skills (LLM-facing instructions), Python scripts (I/O operations), and YAML configuration (model catalogs, routing hints, gate thresholds).

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BRAIN KERNEL                                 │
│  Lifecycle management, pipeline orchestration, component dispatch   │
│  Pipeline: INGEST → DISCOVER → PLAN → ROUTE → EXECUTE → VERIFY    │
│            → COMMIT → LOG                                          │
├─────────────────┬───────────────┬───────────────┬───────────────────┤
│  DISCOVERY      │  ROUTING      │  PLANNING     │  VERIFICATION     │
│  ├ Scanner.py   │  ├ LLM Router │  ├ Planner    │  ├ Gate Runner    │
│  ├ Detectors    │  ├ Specialist │  └ Scheduler  │  ├ Exec Review    │
│  └ Profile Bldr │  └ Provider   │               │  └ Recovery       │
├─────────────────┴───────────────┴───────────────┴───────────────────┤
│  CONTEXT ENGINE       │  MEMORY ENGINE       │  COST OPTIMIZER      │
│  ├ File Selector      │  ├ Profile Store     │  ├ Token Estimator   │
│  ├ Compressor         │  ├ Decision Log      │  └ Budget Advisor    │
│  └ Cache              │  └ Convention Cache  │                      │
├───────────────────────┴──────────────────────┴──────────────────────┤
│  CONFIG MANAGER  │  PLUGIN MANAGER  │  TELEMETRY   │  INSTALLER     │
│  ├ Loader        │  ├ Registry      │  ├ Logger    │  ├ Install      │
│  └ Validator     │  └ Lifecycle     │  └ Doctor    │  ├ Update       │
│                  │                  │              │  └ Uninstall     │
└──────────────────┴──────────────────┴──────────────┴─────────────────┘
```

## Execution Pipeline

```
User Request → INGEST → DISCOVER → PLAN → ROUTE → EXECUTE → VERIFY → COMMIT → LOG
                                                      ↑          │
                                                      └── FAIL ──┘
```

| Stage | Owner | Purpose |
|---|---|---|
| INGEST | Kernel | Classify intent (BUILD/FIX/REFACTOR/ANALYZE/DEPLOY/CREATE) |
| DISCOVER | Project Discovery | Scan workspace, build/load project profile |
| PLAN | Planner | Decompose task into ordered, dependency-aware subtasks |
| ROUTE | LLM Router + Specialist Router | Recommend model, select specialist team |
| EXECUTE | Selected Specialists | Generate solutions in isolation |
| VERIFY | Verification Engine | Run 7 quality gates |
| COMMIT | Memory Engine | Record decisions, present approved result |
| LOG | Telemetry Engine | Record execution trace |

## Module Boundary Rules

- 12 modules, each with exactly one responsibility
- No module performs another module's job (Constitution Article II.6)
- Modules communicate through the Kernel via dispatch, never directly
- Each module owns specific state (Constitution Article IV)

## State Ownership Map

| State | Owner | Location |
|---|---|---|
| Global brain config | Config Manager | `~/.univoid/brain/config/` |
| Project profiles | Memory Engine | `<workspace>/.univoid/memory/` |
| Architectural decisions | Memory Engine | `<workspace>/.univoid/memory/decisions.jsonl` |
| Conventions cache | Memory Engine | `<workspace>/.univoid/memory/conventions.yaml` |
| Execution logs | Telemetry Engine | `~/.univoid/brain/logs/` |
| Plugin registry | Plugin Manager | `~/.univoid/brain/plugins.yaml` |
| Session state | Kernel | In-memory only |

## Component-to-Implementation Mapping

| Module | Skill (.md) | Script (.py) | Config (.yaml) |
|---|---|---|---|
| Kernel | ✅ | — | — |
| Project Discovery | ✅ | ✅ scanner.py | — |
| Context Engine | ✅ | ✅ context.py | — |
| Planner | ✅ | — | — |
| LLM Router | ✅ | — | ✅ models.yaml |
| Specialist Router | ✅ | — | ✅ specialists.yaml |
| Verification Engine | ✅ | — | ✅ gates.yaml |
| Memory Engine | ✅ | ✅ memory.py | — |
| Cost Optimizer | ✅ | — | ✅ costs.yaml |
| Config Manager | — | ✅ config.py | ✅ brain.yaml |
| Plugin Manager | ✅ | ✅ plugins.py | ✅ plugins.yaml |
| Telemetry Engine | — | ✅ telemetry.py | — |

## Dependency Graph

```
Config Manager ← (everything depends on config)
Telemetry Engine ← (everything should log)
Memory Engine ← Discovery, Routing
Project Discovery ← Context Engine, Specialist Router
Context Engine ← Planner
Planner ← Specialist Router
LLM Router ← Cost Optimizer
Specialist Router ← Cost Optimizer, Project Discovery
Verification Engine ← Config (gates.yaml)
Plugin Manager ← Config
Kernel ← ALL (implemented last)
```

## Configuration Hierarchy

```
Level 1 — brain-os/config/*.yaml (shipped defaults, lowest priority)
Level 2 — ~/.univoid/brain/config/*.yaml (user overrides)
Level 3 — <workspace>/.univoid/config/*.yaml (project overrides)
Level 4 — Runtime overrides (highest priority, not persisted)
```

## Platform Constraints

| Constraint | Impact | Workaround |
|---|---|---|
| No programmatic model switching | LLM Router is advisory | Recommend model in trace; adapt to active model |
| No request interception | Brain OS activation not guaranteed | Global AGENTS.md as fallback instruction |
| No token count access | Cost optimization is estimation-based | Advisory cost tracking, not metering |
| No background processes | No persistent daemon | Scripts invoked on-demand; state persists via filesystem |
