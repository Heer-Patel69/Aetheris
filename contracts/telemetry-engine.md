# Module: Telemetry & Logging Engine

## Header
- Name: Telemetry Engine
- Version: 2.1.0
- Purpose: Record execution logs, routing outcomes, and pipeline trace metrics.
- Owner: Telemetry Engine
- Dependencies: Config Manager
- Security Level: MEDIUM
- Performance Target: Write operations complete in <10ms to prevent pipeline blocking.

## Mission
The Telemetry Engine exists solely to record structured execution logs to the global disk cache. It must never intercept, modify, or block system operations.

## Responsibilities
- Write structured JSONL execution traces for every pipeline stage.
- Implement a write-ahead log strategy, saving logs immediately after a stage completes to prevent loss on crashes.
- Record: active model, active specialists, routing confidence scores, verification outcomes, retries, and errors.
- Mask any sensitive user directories or names in paths before writing.
- Support querying logs for debugging and diagnostics.

## Explicitly Forbidden
The Telemetry & Logging Engine MUST NOT:
- Block or delay the main Kernel execution flow (all I/O must be extremely fast or deferred).
- Log credentials, passwords, auth tokens, or code snippets containing secrets.
- Reach out to external networks or telemetry APIs (it is strictly local-only).
- Modify workspace repository files.
- Store user configuration parameters.

## Inputs
- Execution events (stage name, status, duration, active specialists, model, errors)
- Active session ID
- Telemetry path configuration

## Outputs
- Append-only JSONL files in `~/.univoid/brain/logs/`
- Workspace-scoped logs in `<workspace>/.univoid/telemetry/`

## State
- Persistent State: Trace files stored on disk
- Temporary State: Current session trace buffer
- Cache: None
- Configuration: Logging verbosity levels, file size ceilings
- Runtime Variables: Session ID, Workspace root

## Public API
- `Telemetry.LogStageStart(session_id, stage) -> void`
- `Telemetry.LogStageComplete(session_id, stage, metrics) -> void`
- `Telemetry.LogStageFailed(session_id, stage, error) -> void`
- `Telemetry.QueryLogs(filters) -> ArrayOfLogRecords`
- `Telemetry.PruneLogs(older_than) -> void`

## Internal API
- `_writeJSONLine(file_path, data) -> void`
- `_maskSensitiveData(data) -> Dictionary`
- `_checkLogLimits() -> void`

## Event Subscriptions
- On PipelineStarted
- On StageStarted
- On StageCompleted
- On StageFailed
- On PipelineCompleted
- On PipelineAborted

## Events Published
- LogWritten(bytes)
- LogRotationTriggered

## Failure Conditions
- If disk write fails (e.g. disk full):
  Log error to stderr -> disable file-based logging for current session -> fallback to memory-only trace -> continue
- If log file lock encountered:
  Retry once -> fallback to temp log file -> continue

## Quality Standards
- Maximum write latency: 10 ms
- Maximum log directory size: 200 MB (triggers log rotation and pruning)
- Output format: Valid JSON Lines (JSONL) format

## Security Rules
- Scrub all credentials before writing logs.
- Strictly validate log file path parameters to prevent directory traversal.
- Never transmit log data over any network connection.

## Recovery Strategy
Retry once -> Fallback to temporary trace file -> Drop telemetry write -> Continue execution

## Testing Strategy
- Unit Tests: Validate path masking, JSONL structure, and log rotation thresholds.
- Integration Tests: Test log writes under concurrently running threads.
- Stress Tests: Write 10,000 logs in a tight loop and measure latency.
- Performance Tests: Verify write overhead is below 10ms.

## Success Criteria
- Execution trace contains records for all completed pipeline stages.
- Deleting the active workspace does not crash telemetry.
- No secrets are leaked in logs.
