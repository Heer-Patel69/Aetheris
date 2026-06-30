# Module: Plugin Manager

## Header
- Name: Plugin Manager
- Version: 2.1.0
- Purpose: Register, validate, and lifecycle external runtime plugins.
- Owner: Plugin Manager
- Dependencies: Config Manager, Telemetry Engine, Event Bus
- Security Level: CRITICAL
- Performance Target: Plugin loading and manifest validation completed in <100ms.

## Mission
The Plugin Manager exists solely to safely load and coordinate runtime extensions. It is forbidden from executing unvalidated code, bypassing security perimeters, or granting plugins raw database or filesystem access.

## Responsibilities
- Register external plugins and validate their `manifest.yaml` definitions.
- Enforce version compatibility checks between plugins and the Brain OS master version.
- Expose hooks for plugins to subscribe to pipeline stages (e.g., pre-DISCOVER, post-VERIFY).
- Manage plugin state lifetimes (Loaded, Active, Disabled, Error).
- Run diagnostic health checks on plugins during startup.

## Explicitly Forbidden
The Plugin Manager MUST NOT:
- Load or run plugins that do not match the required version contract.
- Grant plugins permission to read/write files outside the workspace perimeter.
- Allow plugins to bypass the Verification Engine.
- Allow plugins to execute system commands without user authorization.
- Modify the global configurations list without validation.

## Inputs
- Global plugin registry file: `~/.univoid/brain/plugins.yaml`
- Individual plugin directory paths containing `manifest.yaml` and source code
- Pipeline hook registration requests

## Outputs
- Plugin status reports (JSON/Dictionary)
- Executed hook payloads returned to the Kernel

## State
- Persistent State: Plugin registry file (`plugins.yaml`)
- Temporary State: Loaded plugin class mappings, active hook subscriber index
- Cache: None
- Configuration: Maximum plugins limit, forbidden plugin directories list
- Runtime Variables: Global plugin installation path

## Public API
- `Plugins.LoadRegistry() -> void`
- `Plugins.RegisterPlugin(plugin_path) -> RegistrationResult`
- `Plugins.ExecuteHook(stage, context) -> HookResult`
- `Plugins.GetPluginStatus(plugin_name) -> PluginStatus`

## Script API (`src/plugins.py`)
- CLI: `python plugins.py --register <path> --output json`
- Output: Standard JSON registration status to stdout

## Event Subscriptions
- On SessionStart
- On WorkspaceOpen

## Events Published
- PluginLoaded(plugin_name, version)
- PluginLoadFailed(plugin_name, error)
- PluginHookExecuted(plugin_name, stage)
- PluginDisabled(plugin_name, reason)

## Failure Conditions
- If plugin manifest validation fails (missing fields or wrong types):
  Publish PluginLoadFailed -> reject plugin -> log error to telemetry -> continue loading remaining plugins
- If plugin throws exception during hook execution:
  Catch exception -> publish PluginDisabled -> mark plugin status as "Error" -> bypass hook -> notify telemetry -> continue
- If plugin version incompatible with Brain OS version:
  Log version conflict -> disable plugin -> publish PluginLoadFailed -> continue

## Quality Standards
- Maximum startup loading latency: 100 ms total for all registered plugins
- Maximum execution overhead: 50 ms max runtime per plugin hook invocation
- Manifest validation must conform to strict JSON Schemas

## Security Rules
- Every plugin must declare its requested permissions in `manifest.yaml`.
- Enforce strict path checks: plugins are forbidden from calling write operations outside `<workspace>/.univoid/`.
- Never load or execute plugin binaries (DLLs, EXEs) — plugins must be Python-only source modules.

## Recovery Strategy
Bypass failed plugin -> Disable plugin in registry -> Re-load safe modules -> Log warning -> Continue execution

## Testing Strategy
- Unit Tests: Verify manifest validation, version comparison, registry reading.
- Integration Tests: Test registering a mock plugin that runs during pre-DISCOVER and verify it alters the context.
- Security Tests: Verify that a plugin attempting to read a path outside the workspace boundary is blocked and disabled.

## Success Criteria
- Plugin Manager correctly registers and executes hooks at the correct pipeline stages.
- Invalid or incompatible plugin manifests are rejected during startup.
- A crashing plugin does not halt the Kernel's main execution loop.
