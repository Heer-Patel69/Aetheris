# Test Plan: Verification Engine

## 1. Scope
This test plan covers syntax checking, quality gate checks, hard/soft rejection rules, and retry limit loops.

## 2. Test Cases

### 2.1 — Successful Verification (Pass)
- **Condition**: Run verification on clean, syntactically correct code matching the plan specifications.
- **Expected Outcome**: All gates return `Pass`. The output is committed.

### 2.2 — Hard Rejection: Secret Detected (Fail / Recovery)
- **Condition**: Verify code containing a plaintext connection string (`postgres://user:pass@host:5432`).
- **Expected Outcome**: The Security gate triggers a hard rejection, logs a security warning, halts execution, and feeds correction requirements to the retry loop.

### 2.3 — Soft Rejection: Code Style Warning (Pass)
- **Condition**: Verify code missing type hints when moderate strictness is active.
- **Expected Outcome**: Maintainability gate records a warning annotation, but the code passes verification and continues.

### 2.4 — Retry Limits Exhausted (Fail)
- **Condition**: specialist repeatedly outputting bad code that fails verification 3 times in a row.
- **Expected Outcome**: Verification Engine halts the pipeline, blocks retry 4, dispatches a `MaxRetriesExhausted` event, and escalates the annotated trace log directly to the user.

## 3. Performance Benchmarks
- Checklists parsing and gate verification MUST complete in **<500ms** (excluding LLM retry generations).
- Syntax parsing on standard source code files must complete in **<50ms**.

## 4. Security Validation Scenarios
- Verify that the Security gate rejects code executing system calls (`os.system`, `subprocess.run`) unless explicitly permitted.
- Verify that code patches do not attempt to write outside the workspace boundaries.