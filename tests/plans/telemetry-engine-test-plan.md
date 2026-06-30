# Test Plan: Telemetry & Logging Engine

## 1. Scope
This test plan covers the verification of writing, masking, and rotating trace logs under multiple pipeline stages.

## 2. Test Cases

### 2.1 — Successful Trace Write (Pass)
- **Condition**: Dispatch pipeline stage events from Kernel.
- **Expected Outcome**: Structured JSONL log records are written to `~/.univoid/brain/logs/execution-trace.jsonl` immediately after each stage completes. Log records contain valid session IDs and JSON structures.

### 2.2 — Path Masking Verification (Pass)
- **Condition**: Pass file system paths containing username folders (e.g. `C:\Users\heerp\project\`) to the logger.
- **Expected Outcome**: Log records substitute the username with a masked pattern (e.g. `C:\Users\<user>\project\`) to protect user privacy.

### 2.3 — Disk Full Handling (Fail / Recovery)
- **Condition**: Mock disk-full exception during trace write.
- **Expected Outcome**: Write failure is caught, error is logged to standard error (`stderr`), file logging is disabled, in-memory log buffer is maintained, and pipeline continues without halting.

### 2.4 — Log Rotation and Pruning (Edge Case)
- **Condition**: Increase log directory size above 200MB.
- **Expected Outcome**: Log rotation is triggered, older files are pruned until directory size drops below 200MB, and a log pruning event is recorded.

## 3. Performance Benchmarks
- Writing a log record to disk MUST complete in **<10ms**.
- Querying telemetry logs for a specific session ID must complete in **<100ms**.

## 4. Security Validation Scenarios
- Verify that no credentials, tokens, or plaintext secrets exist in any logged payloads.
- Test path traversal attempts in log directory settings and verify paths are locked inside the security perimeter.
