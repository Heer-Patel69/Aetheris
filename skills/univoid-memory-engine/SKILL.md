---
name: univoid-memory-engine
description: Caching, conventions indexing, and decision logging engine.
metadata:
  version: v2
  patch: 2.1.0
---

# Memory Engine Skill

## Mission
The Memory Engine exists solely to persist and retrieve project knowledge and global state. It is forbidden from scanning repositories, executing code, or leaking data between workspaces.

## Execution Rules
When state storage operations occur:
1. Invoke the memory script via `python scripts/memory.py` to read or write cache files.
2. Store project-scoped files (cached profiles, ADR decision logs, conventions) strictly in the `<workspace>/.univoid/memory/` directory.
3. Append approved architectural decision records sequentially to `decisions.jsonl`.
4. Validate fingerprint consistency before reloading profiles.
5. If parsing files raises corruption errors, delete the files and trigger re-discovery.

---

> [!IMPORTANT]
> Never write project-specific paths, credentials, or code snippets into the global state directory (`~/.univoid/brain/`). Keep workspace memory directories strictly isolated from one another.
