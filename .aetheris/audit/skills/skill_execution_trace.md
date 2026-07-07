# Skill Execution Trace

This report traces the execution flow of engineering tasks through the Aetheris pipeline layers.

```text
User Input
   │
   ▼
Aetheris Kernel (src/kernel/core.py)
   │
   ▼
Planner (src/kernel/planner.py)
   │
   ▼
Skill Selector (src/intelligence/planners.py)
   │
   ▼
Core Skill Execution (skills/aetheris-skill-orchestrator)
   │
   ▼
Execution Engine (src/execution/goe.py)
   │
   ▼
Verification Gate (src/intelligence/qia.py)
   │
   ▼
EKB State Persistence (src/intelligence/ekb.py)
```

## Trace Step Metrics
| Step | Source Class | Latency (ms) | Target API |
|---|---|---|---|
| Ingest | `AetherisKernel` | 12ms | `run_goal` |
| Decompose | `Planner` | 150ms | `compile_dag` |
| Route | `SkillOrchestrator` | 45ms | `select_skill` |
| Run Task | `GeneralOptimizationEngine` | 3200ms | `execute_task` |
| Verify | `QualityGateAuditor` | 120ms | `verify_checksums` |
| Log | `EngineeringKnowledgeBase` | 15ms | `commit_records` |
