# Module: Project Discovery Engine

## Header
- Name: Project Discovery Engine
- Version: 2.1.0
- Purpose: Build a structured, evidence-based profile of the current workspace without assumptions.
- Owner: Project Discovery Engine
- Dependencies: Config Manager, Telemetry Engine, Event Bus
- Security Level: MEDIUM
- Performance Target: Complete workspace scans in <2 seconds.

## Mission
The Project Discovery Engine exists solely to build an evidence-based profile of the current workspace. It is forbidden from guessing architecture, reading secrets, or executing repository code.

## Responsibilities
- Scan the workspace root (depth limit = 2) for languages, frameworks, package managers, and databases.
- Calculate the workspace fingerprint (SHA-256 hash of directory paths and key configuration files).
- Extract coding conventions and project structure layout from configuration files (tsconfig, postcss, next.config, etc.).
- Package findings into a structured Project Profile matching the defined schema.
- Identify known security/infrastructure risks based on file anomalies (e.g., exposed configuration, missing settings).

## Explicitly Forbidden
The Project Discovery Engine MUST NOT:
- Guess or infer dependencies not documented in workspace files.
- Read `.env`, `.env.local`, or any credential-storing configuration file.
- Modify repository files or execute git mutations.
- Call external APIs to fetch library details.
- Run database migrations or code compilation pipelines.

## Inputs
- Active workspace path
- Configuration parameters (depth limits, ignored directories like `.git`, `node_modules`)
- List of key stack indicator files (`package.json`, `supabase/config.toml`, `Dockerfile`, etc.)

## Outputs
- Structured Project Profile object (JSON/Dictionary)
- Workspace Fingerprint (SHA-256 hash string)

## State
- Persistent State: None (stateless; results are handed to Memory Engine)
- Temporary State: Current directory tree cache
- Cache: None
- Configuration: Ignore directories lists, scan depth limits
- Runtime Variables: Active workspace root

## Public API
- `Discovery.Scan(workspace_path) -> ScanResult`
- `Discovery.CalculateFingerprint(workspace_path) -> Fingerprint`
- `Discovery.DetectLanguages(workspace_path) -> LanguageIndex`

## Script API (`src/scanner.py`)
- CLI: `python scanner.py --workspace <path> --output json`
- Output: Standard JSON to stdout, debug messages to stderr

## Event Subscriptions
- On WorkspaceOpen
- On FileChange

## Events Published
- ProjectProfileReady(profile)
- FingerprintCalculated(hash)
- DiscoveryFailed(reason)

## Failure Conditions
- If directory read fails (permission error):
  Log error to stderr -> skip restricted directory -> decrease scan confidence score -> continue
- If no stack indicator files found:
  Publish ProjectProfileReady with "Stack: Unknown" -> log warning -> continue
- If timeout limit exceeded during scan:
  Halt traversal -> package partial findings -> publish ProjectProfileReady with "Scan: Partial" -> continue

## Quality Standards
- Maximum execution latency: 2,000 ms
- Maximum traversal depth: 2 levels (subdirectories within root)
- Profile schema must match version contract

## Security Rules
- Never read `.env` files or files containing secrets.
- Redact matching key/credential patterns in any config snippet parsed.
- Validate paths to prevent directory traversal outside the workspace perimeter.

## Recovery Strategy
Fallback to cached profile -> Reduce scan depth -> Limit scan to package.json only -> Log warning -> Continue execution

## Testing Strategy
- Unit Tests: Verify scanner logic against mocked file layouts (React+Vite, Python+Django, empty).
- Integration Tests: Verify fingerprint calculation matches after mock workspace file modifications.
- Performance Tests: Verify scan execution completes under 2,000ms on a mock repo with 5,000 files.

## Success Criteria
- Scanner accurately identifies frameworks from package.json dependency keys.
- Scanner detects naming conventions (kebab-case vs CamelCase).
- Fingerprint changes when package.json changes, but remains identical on source code modifications.