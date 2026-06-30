# ADR-005: Memory Separation

## Status
APPROVED

## Context
AI memory systems often suffer from "context contamination" — project-specific details leaking into the global system, or session-level data polluting the long-term project history. We must partition memory into strict layers with distinct lifecycles and invalidation triggers.

## Decision
We partition the Aetheris Kernel memory system into three isolated domains:

```
┌─────────────────────────────────────────────────────────────┐
│ GLOBAL BRAIN STATE (~/.aetheris/)                     │
│ Lifetime: Permanent. Contains: user settings, usage logs   │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ PROJECT STATE (<workspace>/.aetheris/memory/)                │
│ Lifetime: Git-lifecycle. Contains: ADR log, profile cache   │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ SESSION STATE (In-Memory Kernel Context)                    │
│ Lifetime: Single pipeline turn. Contains: active task, retries│
└─────────────────────────────────────────────────────────────┘
```

1. **Global Memory (`~/.aetheris/`)**:
   - Holds metrics (tokens used, run counts), provider profiles, and plugin configurations.
   - Project-specific paths, codebase names, or source code snippets must **never** be written to global memory.

2. **Project Memory (`<workspace>/.aetheris/memory/`)**:
   - Holds the cached Project Profile, the append-only `decisions.jsonl` (ADRs), and `conventions.yaml`.
   - **Staleness Fingerprint**: Calculated as a SHA-256 hash of the directory structure and critical configuration files (e.g., `package.json`, `supabase/config.toml`, `next.config.js`).
   - On workspace initialization, the Memory Engine compares the current fingerprint against the cached fingerprint in `project-profile.yaml`. If they differ, the cache is marked stale and the Discovery Engine is re-run.

3. **Session Memory**:
   - Managed in-memory by the Kernel during a single conversation turn.
   - Holds active specialists, current subtask goals, and gate retry counters.
   - Cleared completely when the final output is committed or aborted.

## Consequences
- Complete safety when moving between repositories — the active model never carries codebase context from one project to another.
- High performance: full directory scans are only triggered when files like `package.json` actually change, otherwise cached profiles are served.
- Telemetry remains global, allowing user usage metrics to be analyzed without exposing code details.

## Alternatives Considered
- **Vector Database**: Storing all project code in a local vector database. *Rejected* because of the excessive dependency overhead (requires compiling native libraries on Windows), high disk usage, and the fact that project profiling does not require semantic search.
- **Git Notes**: Storing decision records directly in git notes. *Rejected* because it requires write access to the git object repository, which violates the security rules of the Constitution (Article VI.5).