# Aetheris Dependency Matrix

| Module | Depends On | Import Type | Boundary Compliance |
|---|---|---|---|
| `src/kernel/core.py` | `runtime`, `enterprise`, `organization`, `learning`, `evolution` | Direct import | Clean |
| `src/intelligence/` | None (independent engines) | Static classes | Clean |
| `src/execution/` | `intelligence.ekb` | State access | Clean |
| `src/runtime/` | None (independent sandbox) | Sandbox executor | Clean |
