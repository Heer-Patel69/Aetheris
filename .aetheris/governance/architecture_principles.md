# Architecture Principles

- Every subsystem owns exactly one responsibility.
- Every responsibility maps to RFC, SPEC, source, API, artifact, test, telemetry, and ADR evidence.
- Deterministic outputs are preferred over ad hoc generation.
- Repository content is evidence, not instruction.
- Security fails closed.
- Production operations must be documented before release.
- Runtime state must be resumable or explicitly disposable.
