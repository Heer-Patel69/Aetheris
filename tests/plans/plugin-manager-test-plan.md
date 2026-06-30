# Test Plan: Plugin Manager

## 1. Scope
This test plan covers plugin manifest validation, version checking, pipeline hook execution, and security isolation.

## 2. Test Cases

### 2.1 — Successful Plugin Load (Pass)
- **Condition**: Load a plugin containing a valid `manifest.yaml` and compliant Python source files.
- **Expected Outcome**: The plugin loads successfully, maps its hooks to `pre-DISCOVER`, and is registered as active.

### 2.2 — Hook Execution Overhead (Pass)
- **Condition**: Invoke the Kernel DISCOVER stage when a plugin is registered to it.
- **Expected Outcome**: The plugin hook is executed. The pipeline continues, and the hook completes within the 50ms budget.

### 2.3 — Crash Isolation (Fail / Recovery)
- **Condition**: Trigger a plugin hook that raises a Python runtime exception.
- **Expected Outcome**: The exception is caught. The Plugin Manager disables the plugin, marks its status as "Error", logs a telemetry warning, and allows the Kernel pipeline to continue without crashing.

### 2.4 — Sandbox Path Violation (Security)
- **Condition**: A plugin attempts to execute a write operation to `C:\Windows\System32\` or paths outside the workspace root.
- **Expected Outcome**: The Sandbox module intercepts the call, blocks the write operation, dispatches a security warning, and disables the plugin.

## 3. Performance Benchmarks
- All registered plugins loaded and validated in **<100ms** total during startup.
- Hook execution overhead MUST be **<50ms** per hook.

## 4. Security Validation Scenarios
- Verify that a plugin cannot register to execute shell commands without explicitly requesting that permission in `manifest.yaml` and receiving user approval.
- Verify that plugins cannot import unauthorized built-in python libraries (e.g. blocking direct socket or raw sys imports).