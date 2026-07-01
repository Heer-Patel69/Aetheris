# Architecture Constraints

- Code generation cannot proceed before planning is complete.
- Modules may not bypass EKB, telemetry, or validation contracts when those are required by their SPEC.
- Secrets must not be persisted in generated documentation or telemetry.
- Planning module decomposition must preserve existing public APIs and tests.
- Execution concurrency must respect dependency graph and file-lock constraints.
- New schemas must map to at least one SPEC and one test.
