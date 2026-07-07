# API Contracts

## WebSocket Events
- `EXECUTION_STARTED`: payload includes intent, models, capabilities.
- `TASK_SCHEDULED`: payload includes DAG node updates.
- `METRIC_UPDATED`: payload includes token usage, latency.
- `LOG_EMITTED`: streaming log lines.