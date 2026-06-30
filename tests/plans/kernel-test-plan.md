# Test Plan: Kernel

## 1. Scope
This test plan covers pipeline lifecycle stage transitions, stage ordering invariants, intent classification, timeout budgeting, and end-to-end execution.

## 2. Test Cases

### 2.1 — Successful End-to-End Pipeline (Pass)
- **Condition**: User submits a standard code modification request.
- **Expected Outcome**: Kernel guides context through all 8 stages sequentially: `INGEST` ➔ `DISCOVER` ➔ `PLAN` ➔ `ROUTE` ➔ `EXECUTE` ➔ `VERIFY` ➔ `COMMIT` ➔ `LOG`.

### 2.2 — Stage Order Invariant Violation (Fail)
- **Condition**: Attempt to trigger the `EXECUTE` stage before the `DISCOVER` stage completes.
- **Expected Outcome**: Kernel blocks the dispatch, registers a pipeline violation, aborts the run, and outputs a hard crash log to Telemetry.

### 2.3 — Stage Timeout Exceeded (Fail / Recovery)
- **Condition**: A module script hangs and exceeds its configured timeout budget.
- **Expected Outcome**: Kernel interrupts execution, records a stage timeout event, skips to `VERIFY` with whatever partial data exists, and logs the warning.

### 2.4 — Lifecycle Mode Matching (Pass)
- **Condition**: Run requests in a brand-new folder vs. a recently-scanned workspace.
- **Expected Outcome**: Correctly matches `COLD_START` (new folder, triggers scanner) and `HOT_PATH` (active session, skips scanner and loads memory cache).

## 3. Performance Benchmarks
- Kernel stage dispatch overhead MUST be **<100ms** per stage.
- Total pipeline latency (excluding LLM reasoning/execution times) must be **<500ms** total.

## 4. Security Validation Scenarios
- Verify that a user cannot bypass pipeline stages (such as verification) by crafting specific prompt inputs.
- Test sandbox path locking of the Kernel scope.
