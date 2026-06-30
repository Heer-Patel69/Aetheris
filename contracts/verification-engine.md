# Module: Verification Engine

## Header
- Name: Verification Engine
- Version: 2.1.0
- Purpose: Enforce quality gates on specialist outputs before delivery.
- Owner: Verification Engine
- Dependencies: Config Manager, Project Discovery, Telemetry Engine, Event Bus
- Security Level: CRITICAL
- Performance Target: Gate verification completed in <500ms.

## Mission
The Verification Engine exists solely to validate specialist outputs. It is forbidden from writing source code, implementing fixes, or softening hard rejections.

## Responsibilities
- Evaluate specialist outputs against 7 distinct quality gates: Architecture, Security, Performance, Maintainability, Accessibility, Business Alignment, and Documentation.
- Run structured checklists representing the CTO, Security Lead, and QA Lead supervisor roles.
- Enforce hard rejection criteria (immediate halt and retry) on critical violations (e.g., hardcoded secrets, syntax errors, security holes).
- Enforce soft rejection criteria (annotate and continue) on minor violations (e.g., missing type hints, missing test stubs).
- Manage the verification retry loop (maximum 3 execution attempts per task).
- Validate merged outputs when multiple specialists contribute code.

## Explicitly Forbidden
The Verification Engine MUST NOT:
- Write source code or auto-fix violations (it only reviews and rejects).
- Soften a hard reject without explicit user authorization.
- Skip any gate or checklist (the execution of all active gates is mandatory).
- Modify git configurations.
- Allow changes outside the active workspace directory.

## Inputs
- Specialist code output (raw text/patch)
- Active Workspace path
- Project Profile (from Memory Engine)
- Target Execution Plan (from Planner)
- Configuration: `gates.yaml` (gate strictness thresholds)

## Outputs
- Gate Validation Result (JSON containing pass/fail status, detailed error annotations with file/line numbers, and retry counts)

## State
- Persistent State: None
- Temporary State: Current session retry counters, active gate reports
- Cache: None
- Configuration: Retry limits (max 3), gate validation checklists
- Runtime Variables: Session ID, active task ID

## Public API
- `Verify.RunGates(output, plan, profile) -> VerificationResult`
- `Verify.VerifyMerge(base_code, patches) -> MergeResult`
- `Verify.IncrementRetry(task_id) -> int`

## Internal API
- `_runCTOGate(code, profile) -> GateResult`
- `_runCSOGate(code) -> GateResult`
- `_runQAGate(code, plan) -> GateResult`
- `_formatRejectionFeedback(gate_results) -> String`

## Event Subscriptions
- On SpecialistOutputReady

## Events Published
- VerificationPassed(output)
- VerificationFailed(annotations, retry_count)
- HardRejectionTriggered(reason)
- MaxRetriesExhausted(task_id)

## Failure Conditions
- If a security check fails (CSO gate fails due to SQL injection or exposed secrets):
  Publish HardRejectionTriggered -> halt execution pipeline -> format strict rejection feedback -> return VerificationFailed -> continue
- If max retries exhausted (retry count > 3):
  Publish MaxRetriesExhausted -> halt pipeline -> escalate output with annotations to the user -> continue
- If code parser fails (syntax error):
  Halt verification -> treat as CTO gate failure -> return VerificationFailed -> continue

## Quality Standards
- Maximum execution latency: 500 ms (excluding LLM retry generation time)
- Maximum retry count: 3 attempts per task step
- Zero tolerance on security rules: 100% of hardcoded secrets must trigger rejections

## Security Rules
- Verification engine must scan for credentials, private keys, and tokens in every patch.
- Verify that code patches do not read/write files outside the workspace perimeter.
- Code analysis must run inside in-memory parser sandboxes.

## Recovery Strategy
Format structured feedback -> Trigger specialist retry loop -> Escalate to user on retry 3 -> Abort pipeline

## Testing Strategy
- Unit Tests: Verify syntax checkers, credential scanner regex, retry loop logic.
- Integration Tests: Test quality gates using mock code containing SQL injection and verify it triggers a hard reject.
- Stress Tests: Validate merging and verifying 10 concurrent specialist patches.
- Performance Tests: Verify execution overhead remains below 500ms.

## Success Criteria
- Verification Engine correctly blocks code containing hardcoded secrets.
- Rejection feedback contains specific file paths, line numbers, and corrective actions.
- Code patches with syntax errors are automatically rejected before delivery to the user.