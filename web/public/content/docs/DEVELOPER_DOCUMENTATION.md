# Aetheris Developer Documentation

## 1. Architecture Directory Structure
* `src/kernel/` — Process management, schedulers, event busses, and telemetry.
* `src/intelligence/` — Prompt compilation, reasoning engines, and context managers.
* `src/execution/` — Code generation, git execution, self-reviews, and metric engines.
* `src/runtime/` — Sandboxing, IPC/RPC, and cluster registries.
* `src/learning/` — Experience loggers and success rankers.
* `src/enterprise/` — Auth platforms, RBAC, and multi-tenant quotas.
* `src/organization/` — Stateful persona agents (CEO, CTO, Developer).
* `src/evolution/` — Self-evolution orchestrator and AST refactoring engines.

## 2. Extending the Platform
To register a new execution component:
1. Implement the class under a subfolder of `src/`.
2. Hook its initialization into the `AetherisKernel.__init__` constructor inside `src/kernel/core.py`.
3. Add a corresponding compliance unit test to `tests/test_all_specs_compliance.py`.
