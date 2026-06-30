# Module: Memory Engine

## Header
- Name: Memory Engine
- Version: 2.1.0
- Purpose: Persist, retrieve, and manage global settings and project-scoped state (caching, decision logs, conventions).
- Owner: Memory Engine
- Dependencies: Config Manager, Telemetry Engine, Event Bus
- Security Level: CRITICAL
- Performance Target: Read operations <50ms; write operations <100ms.

## Mission
The Memory Engine exists solely to persist and retrieve project knowledge and global state. It is forbidden from scanning repositories, executing code, or leaking data between workspaces.

## Responsibilities
- Manage the lifecycles of Global Memory, Project Memory, and Session Memory.
- Cache project profiles, ADR decision logs (`decisions.jsonl`), and discovered conventions (`conventions.yaml`).
- Validate cache staleness using workspace fingerprints (SHA-256 hash calculated by the Discovery Engine).
- Detect and recover from state file corruption.
- Enforce strict workspace isolation boundaries on disk.

## Explicitly Forbidden
The Memory Engine MUST NOT:
- Scan the directory tree or infer project structures (that is the Discovery Engine's job).
- Make routing choices or planning decisions.
- Leak metadata or code snippets from one workspace to another.
- Modify repository-tracked codebase files.
- Execute external executables or commands.

## Inputs
- State storage paths (Global: `~/.aetheris/`, Project: `<workspace>/.aetheris/memory/`)
- Project profiles, ADR records, and coding conventions
- Workspace fingerprint hashes

## Outputs
- Cached Project Profile (YAML)
- ADR Decision List (JSONL)
- Coding standards conventions (YAML)
- Cache validity state (Valid/Stale/Missing)

## State
- Persistent State: Project profile cache, decision log, conventions cache
- Temporary State: Current session workspace mapping, read cache dictionary
- Cache: In-memory memory structures to avoid repeated disk reads
- Configuration: Fingerprint criteria rules, cache expiration ceilings
- Runtime Variables: Active workspace root, active fingerprint

## Public API
- `Memory.GetProfile(workspace_path) -> ProjectProfile`
- `Memory.SaveProfile(workspace_path, profile) -> void`
- `Memory.GetDecisions(workspace_path) -> ListOfADRs`
- `Memory.SaveDecision(workspace_path, adr_record) -> void`
- `Memory.GetConventions(workspace_path) -> Conventions`
- `Memory.SaveConventions(workspace_path, conventions) -> void`
- `Memory.VerifyFingerprint(workspace_path, current_fingerprint) -> bool`

## Internal API
- `_checkCacheCorrupted(file_path) -> bool`
- `_resolvePath(workspace_path, relative_path) -> Path`
- `_purgeUnusedCaches() -> void`

## Event Subscriptions
- On WorkspaceOpen
- On MemoryUpdated
- On ProjectProfileReady

## Events Published
- MemoryLoaded(workspace_path)
- CacheInvalidated(reason)
- MemoryWriteCompleted(type)
- CacheCorrupted(file_path)

## Failure Conditions
- If profile JSON/YAML parsing fails (corrupted cache):
  Publish CacheCorrupted -> delete corrupted file -> invalidate cache state -> trigger ProjectProfileReady subscription to rebuild -> continue
- If write permission denied on workspace path:
  Log error -> fallback to global directory caching (using workspace hash namespace) -> notify telemetry -> continue
- If fingerprint mismatch:
  Publish CacheInvalidated -> mark cache stale -> dispatch ProjectProfileReady event -> continue

## Quality Standards
- Maximum read latency: 50 ms
- Maximum write latency: 100 ms
- Serialization format: YAML for profiles/conventions, JSONL for decisions
- State schema version must match SemVer version contract

## Security Rules
- Restrict read/write operations strictly to paths starting with the approved perimeter (c:/.aetheris or workspace/.aetheris).
- Redact secrets before serializing memory fields.
- Isolate workspace memory directories: enforce file access controls so one project cannot access another's memory directory.

## Recovery Strategy
Delete corrupted file -> Re-verify workspace -> Query Discovery Engine to rebuild cache -> Log warning -> Continue execution

## Testing Strategy
- Unit Tests: Verify JSONL file append operations, YAML serializations, fingerprint checks.
- Integration Tests: Test cache invalidation when a mockup package.json changes.
- Security Tests: Attempt to read configuration from a sibling workspace path and verify it fails path verification checks.

## Success Criteria
- Memory Engine correctly detects stale cache after package.json matches a different hash.
- ADR logs are appended without corruption.
- Deleting the repository memory folder does not halt Kernel initialization.