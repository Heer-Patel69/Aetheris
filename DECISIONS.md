# Aetheris Kernel — Architecture Decisions

**Version**: 2.0.0

---

## Decision Log

| # | Decision | Reason | Alternatives Rejected | Trade-offs | Status |
|---|---|---|---|---|---|
| D-001 | Source lives at `c:\AI\Agency owner\aetheris\` | Keeps Aetheris Kernel alongside the Agency roster it orchestrates | Dedicated `c:\AI\brain-os\`; home dir `~\.aetheris\brain-os\` | Couples source to agency-agents workspace | APPROVED |
| D-002 | Clean replacement of v1.0 (no fallback) | v2.0 is architecturally incompatible; running both causes confusion | Keep v1.0 as fallback during transition | No rollback without manual reinstall | APPROVED |
| D-003 | Installer creates global `AGENTS.md` | Only mechanism for always-activate behavior in Antigravity | Manual activation; no global rules | May affect non-Brain-OS conversations | APPROVED |
| D-004 | Separate `aetheris-*` skill names (not one monolithic skill) | Each module has distinct trigger surface; prevents loading entire runtime | Single `aetheris-brain-os` skill with deep references | More files to manage; more install complexity | APPROVED |
| D-005 | Software Constitution approach (not feature-list) | Invariants prevent scope creep; formal specs catch design errors before code | Feature-list implementation plan (rejected by user) | Higher upfront specification cost | APPROVED |
| D-006 | 8-phase strict implementation (no skipping) | Prevents "generate and organize later" anti-pattern | Single-pass generation (rejected by user) | Slower time-to-working-code | APPROVED |
| D-007 | Kernel implemented last (Phase 5l) | Depends on all module interfaces being stable | Kernel first (would require interface changes later) | Can't test full pipeline until all modules exist | APPROVED |
| D-008 | Python-only scripts (no bash) | Windows compatibility; bash not installed on user's system | Bash scripts (failed — not available) | Limits to Python ecosystem; no shell pipelines | APPROVED |
| D-009 | No fixed specialist ceiling (dynamic team sizing) | Complex tasks need more than 3 specialists; simple tasks need fewer | Fixed ceiling of 3 (v1.0 approach, explicitly rejected by user) | More specialists = more context = higher cost | APPROVED |
| D-010 | Scoring weights: Intent 0.35, Stack 0.25, Risk 0.15, Context 0.15, Cost 0.10 | Balanced emphasis on intent match with cost/context signals | v1.0 weights (0.5/0.3/0.2 — no cost/context) | May need tuning based on real-world usage | APPROVED |

| ADR-001 | Module Boundaries | Instruction vs execution separation rules | Pure Prompt Model; Pure Python Wrapper | Keeps context clean, enables unit testing | APPROVED |
| ADR-002 | State Ownership | Single Owner Principle for global/project/session state | Global SQLite; Git-based state | Prevents concurrency writes, ensures isolation | APPROVED |
| ADR-003 | Event Model | Stateless Event Propagation Broker in Kernel | File-based Event Queue; Direct imports | Decouples modules, runs within execution loop | APPROVED |
| ADR-004 | Configuration Hierarchy | 4-tier merging deep override rules (user > defaults) | Environment Variables only; single big YAML | Standardized override patterns, commits safe | APPROVED |
| ADR-005 | Memory Separation | Global vs project partition; fingerprint invalidation | Vector Database; Git notes | Zero context leaks, re-scans only on package.json change | APPROVED |
| ADR-006 | Skill Decomposition | Decomposing runtime into 8 distinct global skills | Monolithic `aetheris-brain-os` skill; local configs | Minimizes loaded context, allows stage-level updates | APPROVED |
| ADR-007 | Script Execution Model | Command line args input, JSON stdout, exit code 0 | Standard Text stdout; WebSocket IPC | Easy LLM parsing, shell clean, error-safe | APPROVED |
| ADR-008 | Version Contract | Semantic Versioning 2.0.0, schema compatibility | Commit hashes; per-module versioning | Clean upgrades, fails safe on legacy caches | APPROVED |
| ADR-009 | Platform Constraints | Advisory routing, best-effort rules, token estimation | Custom wrapper CLI executable | Sandboxed safety, adapts dynamically to active model | APPROVED |
| ADR-010 | Security Perimeter | Path boundaries, secret redaction, no user deletion | Docker containerization | Prevents file loss, security audit compliant | APPROVED |
| ADR-011 | Autonomous Software Engineering OS | Redesigning modules into 8 consolidated core engines (PAIE, RCIE, ESRE, MKLE, AOL, UAL, RSC, Kernel) with topological Task DAG scheduler, tech decisions engine, uncertainty discovery, resource manager, autonomous recovery, and Definition of Done checks | 20+ fragmented modules; flat unorganized scripts | Reduces code redundancy, enables parallel execution, builds production-ready systems autonomously | APPROVED |
