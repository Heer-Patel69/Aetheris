# ADR-003: Event Model

## Status
APPROVED

## Context
In a standard operating system, modules communicate via asynchronous message passing, RPCs, or an event bus. Since Antigravity does not support a running daemon (scripts are executed on-demand and terminate immediately), we need a design pattern to pass events and state changes between modules without creating tight coupling.

## Decision
We implement a **Stateless Event Propagation Model** managed by the Kernel during its pipeline execution loop:

1. **Pipeline Event Bus**:
   - The Kernel serves as the orchestrator and the message broker.
   - When a Python script (e.g., `scanner.py`) executes, it returns a JSON object. This object can contain an `events_published` array.
   - Example output:
     ```json
     {
       "status": "success",
       "data": { ... },
       "events_published": [
         { "type": "ProjectProfileReady", "payload": { "fingerprint": "xyz" } }
       ]
     }
     ```

2. **Event Routing**:
   - The Kernel parses the JSON output of each executed stage.
   - If `events_published` is present, the Kernel appends the events to a session queue.
   - Before dispatching the next pipeline stage, the Kernel checks the subscriber lists in `specialists.yaml` or module manifests, and injects the event payloads into the input arguments of the target modules.

3. **Event Declarations**:
   - Every module contract must explicitly define the events it publishes and subscribes to.
   - If a module publishes an undeclared event, the Kernel must discard it and log an invariant violation.

## Consequences
- Modules remain completely decoupled from each other. The Project Discovery module doesn't know that the Memory Engine exists; it simply publishes `ProjectProfileReady`, and the Kernel handles routing it.
- Debugging is simple because the entire event stream is captured sequentially in the telemetry log.

## Alternatives Considered
- **File-based Event Queue**: Writing events to an append-only JSON file at `~/.univoid/brain/events.json` and polling it. *Rejected* because it causes excessive disk I/O, risks race conditions on concurrent executions, and is unnecessary since all execution is orchestrated sequentially by the Kernel.
- **Direct Module Invocation**: Allowing Python scripts to directly import and call functions from other scripts. *Rejected* because it creates a monolithic codebase and violates the single responsibility principle.
