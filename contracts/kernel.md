# Module: Kernel

## Header
- Name: aetheris-kernel
- Version: 2.1.0
- Purpose: Coordinate the execution lifecycle without performing any specialist work.
- Owner: Aetheris Kernel
- Dependencies: None (all other modules depend on Kernel)
- Security Level: CRITICAL
- Performance Target: <100ms overhead per pipeline stage dispatch.

## Mission
The Kernel exists solely to coordinate the execution lifecycle. It never generates code, never reasons about implementation, and never selects specialists. It only dispatches, schedules, and supervises.

## Responsibilities
- Own the execution pipeline lifecycle (INGEST ➔ DISCOVER ➔ PLAN ➔ ROUTE ➔ EXECUTE ➔ VERIFY ➔ COMMIT ➔ LOG).
- Dispatch execution requests to the correct module at each stage.
- Enforce strict stage ordering invariants.
- Manage session state and active context objects.
- Handle lifecycle modes (COLD_START, WARM_START, HOT_PATH).
- Publish lifecycle events.
- Enforce timeout budgets per stage.

## Explicitly Forbidden
The Kernel MUST NOT:
- Generate code or code patches.
- Reason about implementation details.
- Select specialists (that belongs to the Resource Router).
- Select models (that belongs to the Resource Router).
- Read repository files directly (that belongs to the Discovery Engine).
- Modify repository files.
- Make architectural decisions.
- Skip any pipeline stage.
- Bypass verification.
- Expose internal state to external consumers.
- Handle recovery for other modules (each module owns its recovery).

## Inputs
- User request (raw text)
- Active workspace path
- Session state (if warm/hot start)
- Configuration (from Config Manager)

## Outputs
- Pipeline execution trace
- Final approved response
- Updated session state
- Telemetry events

## State
- Persistent: None (stateless across sessions)
- Temporary: Current pipeline stage, active task ID, retry counters, session variables
- Cache: None
- Configuration: Pipeline stage ordering, timeout budgets, stage strictness rules
- Runtime: Lifecycle mode (COLD/WARM/HOT)

## Public API
- `Kernel.Ingest(request) -> ClassifiedIntent`
- `Kernel.Dispatch(stage, context) -> StageResult`
- `Kernel.GetPipelineState() -> PipelineState`
- `Kernel.Abort(reason) -> void`

## Internal API
- `_classifyIntent(request) -> IntentType`
- `_determineLifecycleMode(workspace) -> LifecycleMode`
- `_enforceStageOrder(current, next) -> bool`
- `_checkTimeout(stage, elapsed) -> bool`

## Event Subscriptions
- On SessionStart
- On WorkspaceChanged
- On ModuleFailure(module, error)

## Events Published
- PipelineStarted(intent, lifecycle_mode)
- StageStarted(stage)
- StageCompleted(stage, result)
- StageFailed(stage, error)
- PipelineCompleted(result)
- PipelineAborted(reason)

## Failure Conditions
- If module dispatch fails:
  Retry once -> abort stage -> publish StageFailed -> request clarification -> halt pipeline
- If stage timeout exceeded:
  Abort stage -> publish StageFailed -> skip to VERIFY with partial results -> continue
- If pipeline stage order violated:
  Hard abort -> publish PipelineAborted -> report invariant violation to user
- If all retries exhausted:
  Abort pipeline -> present partial results with explanation

## Quality Standards
- Maximum dispatch latency: 100 ms per stage
- Maximum pipeline overhead: 500 ms total (excluding module execution time)
- Maximum retry count: 2 per stage
- Pipeline must complete or abort within configured timeout

## Security Rules
- Never execute user-provided code.
- Never read files outside the active workspace.
- Never modify the Aetheris Kernel installation.
- Never expose session state to other sessions.
- Never bypass the verification stage.

## Recovery Strategy
Retry dispatch -> Skip failed stage with annotation -> Reduce pipeline (skip non-critical stages) -> Present partial results -> Abort with explanation

## Testing Strategy
- Unit: Stage ordering invariants, lifecycle mode detection, intent classification.
- Integration: Full pipeline execution with mock modules.
- Stress: Rapid workspace switching, concurrent requests.
- Security: Attempt to skip stages, inject unauthorized commands.

## Success Criteria
- Every request enters INGEST.
- Every request exits through either COMMIT or ABORT.
- No stage is ever skipped without explicit annotation.
- Pipeline trace is always available in telemetry.
- Kernel never generates content — only coordinates.