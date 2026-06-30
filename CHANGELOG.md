# UniVoid Brain OS — Changelog

All notable changes to the UniVoid Brain OS will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] — 2026-06-30

### Added
- **11 Module Contracts**: Created and saved formal module contracts under [brain-os/contracts/](file:///c:/AI/Agency%20owner/brain-os/contracts) for config-manager, telemetry-engine, event-bus, memory-engine, project-discovery, context-engine, planner, resource-router, verification-engine, plugin-manager, and kernel.
- **Event Bus Specifications**: Added detailed event brokering, priority queuing, and dead-letter handling to the message contracts.

### Changed
- **Subsystem Mergers**:
  - Merged **Cache Engine** into the **Memory Engine** to consolidate data storage.
  - Merged **LLM Router** and **Cost Optimizer** into the **Resource Router** to link model recommendation to token budgets.
- **Directory Layout Refactor**: Updated the implementation plan to establish a 3-layer directory structure: Layer 1 (Global Runtime: `~/.univoid/`), Layer 2 (Source Code: `UniVoid-Brain-OS/`), and Layer 3 (Per-Project State: `.univoid/`).
- **Roadmap Shift**: Shifted current phase to Phase 3 (Configuration Schemas).

## [2.0.0] — 2026-06-30


### Added
- **System Constitution**: Created [00_SYSTEM_CONSTITUTION.md](file:///c:/AI/Agency%20owner/brain-os/00_SYSTEM_CONSTITUTION.md) detailing the supreme vision, non-negotiable principles, module ownership, and execution guidelines.
- **Architecture Decision Records**: Authored 10 ADRs ([001](file:///c:/AI/Agency%20owner/brain-os/adrs/001-module-boundaries.md) through [010](file:///c:/AI/Agency%20owner/brain-os/adrs/010-security-perimeter.md)) under `brain-os/adrs/` defining boundaries, state, events, config overrides, skill splitting, execution contracts, and sandbox perimeters.
- **Repository State Files**: Setup workspace tracking files: [PROJECT_STATE.md](file:///c:/AI/Agency%20owner/brain-os/PROJECT_STATE.md), [ARCHITECTURE.md](file:///c:/AI/Agency%20owner/brain-os/ARCHITECTURE.md), [DECISIONS.md](file:///c:/AI/Agency%20owner/brain-os/DECISIONS.md), [TASKS.md](file:///c:/AI/Agency%20owner/brain-os/TASKS.md), [MEMORY.md](file:///c:/AI/Agency%20owner/brain-os/MEMORY.md), and [NEXT_SESSION.md](file:///c:/AI/Agency%20owner/brain-os/NEXT_SESSION.md).
- **Agency Skill Migration**: Converted and installed the 217 Agency specialists into the global Antigravity configuration directory under `agency-*` namespaces.

### Changed
- **Architecture Paradigm**: Transitioned the Brain OS specification from an LLM prompt (v1.0 instructions) to a structured software runtime architecture (v2.0 System Constitution).
