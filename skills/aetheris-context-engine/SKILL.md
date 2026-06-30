---
name: aetheris-context-engine
description: Context selection, token optimization, and code compression engine.
metadata:
  version: v2
  patch: 2.1.0
---

# Context Engine Skill

## Mission
The Context Engine exists solely to determine the minimum information required for the current reasoning task. It is forbidden from making architectural decisions, routing specialists, or editing code.

## Execution Rules
When context selection is requested:
1. Invoke the context script via:
   `python scripts/context.py --workspace <path> --task <task_description>`
2. The script filters workspace files by relevance to task keywords, extracts public signatures from files larger than 20KB, redacts secrets, and computes token counts.
3. Parse the output JSON Package.
4. Load the selected, compressed context payload into the active LLM reasoning frame.

---

> [!WARNING]
> Keep the total context budget under 20,000 tokens for simple tasks. Verify that all file paths returned are strictly within the workspace perimeter.