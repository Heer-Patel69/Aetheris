# ADR-002: State Ownership

## Status
APPROVED

## Context
A state-sharing system without strict ownership guarantees leads to concurrency conflicts, out-of-order writes, configuration drift, and security leaks. We need to define exactly which module owns which piece of state, where that state is saved, and how isolation is enforced.

## Decision
We establish the **Single Owner Principle** for all persistent and runtime state:

1. **State Partitioning and File Paths**:
   - **Global State** (`~/.aetheris/`): Owned by the **Configuration Manager** (configs) and **Plugin Manager** (plugins). Contains user global preferences, the model catalog, and plugin configurations.
   - **Project State** (`<workspace>/.aetheris/memory/`): Owned by the **Memory Engine**. Contains project profiles, the ADR decision log, and conventions cache.
   - **Telemetry State** (`~/.aetheris/logs/`): Owned by the **Telemetry Engine**. Contains execution trace files.
   - **Session State** (In-Memory): Owned by the **Kernel**. Tracks active pipeline stage, retry counts, and currently active task context.

2. **Access Rules**:
   - **Mutations (Writes)**: Only the owning module may write to its designated state files. No other module or script may execute writes. For example, the Discovery Engine cannot write the project profile; it must output the profile JSON, which is then passed to the Memory Engine to write.
   - **Queries (Reads)**: Other modules may read state through public APIs exposed by the owning script or through the Kernel's dispatch context.
   - **Isolation Boundary**: When switching workspaces, the Memory Engine must completely unload the previous project profile. Project directories (`.aetheris/memory/`) must never be accessible across workspaces.

## Consequences
- Prevents write conflicts because only a single Python script writes to any single directory.
- Ensures clean workspace transitions because all project-scoped state is strictly isolated within the workspace's `.aetheris/` directory.
- Simplifies telemetry because the Telemetry Engine is the sole writer of the log stream.

## Alternatives Considered
- **Centralized Database**: Storing all project state in a global SQLite database at `~/.aetheris/state.db`. *Rejected* because it creates a single point of failure, complicates backup/migration of project directories, and risks leaking project profiles if database files are shared.
- **State in Git**: Storing decisions and profiles directly in the project's standard files (like README or a wiki). *Rejected* because the runtime must not modify user-managed files without explicit commands, and state should be kept in a dedicated namespace (`.aetheris`).