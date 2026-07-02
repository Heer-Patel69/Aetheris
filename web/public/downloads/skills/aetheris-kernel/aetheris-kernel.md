---
name: aetheris-kernel
description: Master pipeline orchestrator and execution lifecycle controller for Aetheris Kernel.
metadata:
  version: v2
  patch: 2.1.0
---

# Aetheris Kernel

## Mission
The Aetheris Kernel exists solely to coordinate the execution lifecycle. It never generates code, never reasons about implementation, and never selects specialists. It only dispatches, schedules, and supervises.

## Operational Constitution
Every execution MUST run through the Aetheris Kernel v3.0 dynamic Task DAG lifecycle:

1. **Ingest & Discover**:
   - Check if project fingerprint matches cache. If stale/missing, run scanner:
     `python scripts/scanner.py --workspace <path> --output json`
   - Detect framework conventions, project memory, and resource limits.

2. **Product Discovery & Tech Decisions (PAIE)**:
   - Identify critical uncertainties and request clarification.
   - Run Technology Decision checks and generate structural architecture blueprints.

3. **Context Compilation (RCIE)**:
   - Run semantic graph traversal to select only necessary files.
   - Inject project memory and enhance local models when applicable.

4. **Task DAG Assembly & Execution**:
   - Build a topological Directed Acyclic Graph (DAG) of tasks.
   - Execute independent steps in parallel.
   - If a build/compile error is encountered, trigger the Autonomous Recovery Loop:
     `Compile Error ➔ RCA Analysis ➔ Code Repair ➔ Rebuild ➔ Rerun Verify`

5. **Definition of Done Verification (ESRE)**:
   - Run quality standards check (SOLID, Clean Architecture, OWASP, Accessibility).
   - Validate strict Definition of Done (DoD) criteria (coverage, secrets check, deployments).

6. **Memory Commit & Benchmarking (MKLE)**:
   - Record approved decisions to `.aetheris/memory/decisions.jsonl`.
   - Log latency, token count, and performance scores for self-learning.

---

> [!IMPORTANT]
> The Kernel must never skip the Verification stage or execute raw shell scripts outside the approved sandbox. If any error is encountered, execute the Autonomous Recovery Loop first before presenting failures to the user.