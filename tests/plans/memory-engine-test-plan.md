# Test Plan: Memory Engine

## 1. Scope
This test plan covers cache read/write performance, fingerprint checks, corruption self-healing, and project state isolation.

## 2. Test Cases

### 2.1 — Cache Read/Write (Pass)
- **Condition**: Read and write project profiles and decisions.
- **Expected Outcome**: Profile is serialized and stored in `.univoid/memory/project-profile.yaml` and retrieved in <50ms.

### 2.2 — Fingerprint Validation (Pass)
- **Condition**: Calculate a fingerprint and compare it against the cached fingerprint in a workspace.
- **Expected Outcome**: Returns `true` if identical, `false` if files were modified (marking cache stale).

### 2.3 — Corruption Self-Healing (Fail / Recovery)
- **Condition**: Write a corrupted JSON structure to `decisions.jsonl`.
- **Expected Outcome**: Memory Engine catches the parsing exception, deletes the corrupted file, dispatches a `CacheCorrupted` event, and allows the Discovery Engine to rebuild state.

### 2.4 — Workspace Isolation (Security / Boundary)
- **Condition**: Attempt to read memory state from a sibling workspace path using directory traversal (`../../other-project/.univoid/`).
- **Expected Outcome**: Memory Engine blocks the request, logs path violation, and returns permission error.

## 3. Performance Benchmarks
- Memory read latency: **<50ms**.
- Memory write latency: **<100ms**.
- Fingerprint validation check: **<100ms**.

## 4. Security Validation Scenarios
- Verify that credentials are redacted before writing memory files.
- Test that read/write operations are strictly restricted to paths within the security perimeter.
