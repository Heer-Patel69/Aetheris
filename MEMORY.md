# Aetheris Kernel — Memory State

**Version**: 3.0.0
**Project**: Permanent AI Orchestration Runtime for Antigravity

---

## Developer / User Profile
- **Handle**: heerp (username: Univoid)
- **Engineering Preference**: Senior distributed systems and systems architecture mindset.
- **Values**: Formal specifications, MUST/MUST NOT constraints, clean module separation, structural predictability, strict implementation phase ordering (no code before plans/schemas are approved).
- **Explicit Dislikes**: Ad-hoc prompts, vague instructions, monoliths, responsibility creep, hallucinated project structures.

## Technical Assumptions
- **Host IDE**: Antigravity (Google DeepMind AI agent).
- **Language**: Python 3.14 for scripts, Markdown for skills and reference files.
- **OS**: Windows (PowerShell environment, no native bash available).
- **Skill Directory**: Global installation target is `C:\Users\heerp\.gemini\config\skills\`.
- **App Data Directory**: `C:\Users\heerp\.gemini\antigravity-ide\`.

## Architectural Rules
1. **Instruction vs. Execution Separation**: LLM dispatches and coordinates via skills/references; filesystem modifications, calculations, and hashing are handled by Python scripts (ADR-001).
2. **Single Owner**: Only the designated module may write to its state directory (ADR-002).
3. **Stateless Kernel Execution**: Event bus resides in the pipeline loop context, passed through JSON outputs (ADR-003).
4. **4-Tier Merge**: Config overrides merge deep recursively: Tier 1 (defaults) -> Tier 2 (shipped defaults) -> Tier 3 (user global) -> Tier 4 (project local) (ADR-004).
5. **Memory Partitioning**: Global settings, project profiles, and session variables are kept strictly separate; project profiles invalidate using fingerprints (ADR-005).
6. **Skill Splitting**: Decompose runtime into 8 distinct global skills to reduce context bloat (ADR-006).
7. **Execution Contract**: Scripts take CLI flags, output JSON to stdout, print info to stderr, exit with code 0 on success (ADR-007).
8. **Semantic Versioning**: Standard SemVer 2.0.0 for matching files and caches (ADR-008).
9. **Platform Workarounds**: LLM Router is advisory; Kernel uses global AGENTS.md rules for activation; Cost Optimizer estimates tokens via string heuristics (ADR-009).
10. **Perimeter Controls**: Sandbox reads workspace + config + brain state paths only; RLS/credentials must be redacted; no file deletion allowed (ADR-010).
11. **Autonomous ASE-OS Pipeline**: Runs topological Task DAGs concurrently, checks resource manager constraints, implements uncertainty discovery queries, runs autonomous RCA recovery loops, and verifies the strict Definition of Done (DoD) before committing tasks (ADR-011).