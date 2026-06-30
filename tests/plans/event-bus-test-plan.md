# Test Plan: Event Bus

## 1. Scope
This test plan covers event subscription registration, priority dispatching, payload validation, and subscriber isolation.

## 2. Test Cases

### 2.1 — Successful Event Dispatch (Pass)
- **Condition**: Register a subscriber for `ProjectProfileReady` and publish the event with a valid payload.
- **Expected Outcome**: The subscriber's handler is called with the correct payload in FIFO order.

### 2.2 — Priority Dispatching (Pass)
- **Condition**: Publish a `CRITICAL` priority event and a `LOW` priority event simultaneously.
- **Expected Outcome**: The `CRITICAL` event is dispatched and handled before the `LOW` event.

### 2.3 — Handler Exception Isolation (Fail / Recovery)
- **Condition**: A subscriber's handler throws an unhandled exception.
- **Expected Outcome**: Event Bus catches the error, registers it as a dead-letter, publishes a `DeadLetterLogged` event, and continues to dispatch other subscribers without crashing.

### 2.4 — Schema Validation Failure (Fail)
- **Condition**: Publish an event with a payload that does not match the registered schema.
- **Expected Outcome**: Event Bus rejects the event, logs a schema error to the dead-letter queue, and does not notify subscribers.

## 3. Performance Benchmarks
- Event routing and dispatching MUST complete in **<5ms** per event.
- Concurrent dispatching of 1,000 events must complete in **<100ms** total.

## 4. Security Validation Scenarios
- Verify that a module cannot subscribe to restricted kernel lifecycle events.
- Test that event payloads cannot carry executable scripts or context injection code.
