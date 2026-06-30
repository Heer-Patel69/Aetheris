---
name: univoid-project-discovery
description: Workspace directory sweep and framework detection engine for UniVoid Brain OS.
metadata:
  version: v2
  patch: 2.1.0
---

# Project Discovery Skill

## Mission
The Project Discovery Engine exists solely to build an evidence-based profile of the current workspace. It is forbidden from guessing architecture, reading secrets, or executing repository code.

## Execution Rules
When triggered or dispatched by the Kernel:
1. Run the workspace scanner script via:
   `python scripts/scanner.py --workspace <active_workspace_path> --output json`
2. Parse the JSON profile returned on standard output.
3. Extract:
   - Languages and framework targets
   - Conventions (naming conventions, styling libraries, testing frameworks)
   - Configuration hashes (fingerprint)
4. Record findings and pass the Project Profile to the Memory Engine to cache in `.univoid/memory/project-profile.yaml`.

---

> [!WARNING]
> Do not search deeper than 2 levels of subfolders. Do not read files named `.env` or any file containing active credentials. If files are missing, record "unknown stack" without making assumptions.
