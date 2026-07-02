---
name: aetheris-skill-orchestrator
description: Scoring and selection engine for LLM models and specialized Agency agents.
metadata:
  version: v2
  patch: 2.1.0
---

# Routing Engine Skill

## Mission
The Resource Router selects the minimum effective specialist team and recommends the optimal model. It is forbidden from programmatically switching models, executing tasks, or verifying outputs.

## Execution Rules
When routing is dispatched:
1. Query the **Dynamic Registry** to get all dynamically discovered Agency and custom skills (ADR-005). Do NOT rely on static YAML files.
2. Load the active Project Profile and Task Intent from workspace memory.
3. Perform capability matching by intersecting Task Requirements with skill fields: `capabilities`, `languages`, `frameworks`, and `keywords`.
4. Calculate the confidence score ($S$) for candidate specialists:
   `S = (CapabilityMatch * 0.40) + (LanguageRelevance * 0.20) + (FrameworkRelevance * 0.20) + (ContextFit * 0.10) + (CostEfficiency * 0.10)`
5. Select all specialists scoring $S \ge 80$. If no specialist scores above 80, default to Kernel generalist mode.
6. Assemble a dynamic Execution Team (1-2 specialists for Trivial tasks, 3-5 for Medium tasks, 6-10 for Large tasks).
7. Query `config/models.yaml` and `config/costs.yaml` to evaluate active model requirements and estimate run costs.
8. Present the routing roster and estimated costs in the trace before execution begins.

---

> [!NOTE]
> Specialist routing is dynamic. Keep teams minimal. Dynamically adapt team size based on task complexity.
