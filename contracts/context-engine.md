# Module: Context Engine

## Header
- Name: Context Engine
- Version: 2.1.0
- Purpose: Select, optimize, and compress workspace context for the current reasoning task.
- Owner: Context Engine
- Dependencies: Config Manager, Project Discovery, Telemetry Engine, Event Bus
- Security Level: HIGH
- Performance Target: Context collection completed in <200ms.

## Mission
The Context Engine exists solely to determine the minimum information required for the current reasoning task. It is forbidden from making architectural decisions, routing specialists, or editing code.

## Responsibilities
- Analyze user task context and select the minimal set of relevant source code files.
- Perform regex-based token estimation to stay within the model's budget.
- Compress large files into signature maps (e.g., extracting functions, exports, and classes instead of full files).
- Keep context lean by filtering out build folders, binary files, and node_modules.
- Track import dependencies to ensure dependent types/modules are included when necessary.

## Explicitly Forbidden
The Context Engine MUST NOT:
- Select specialists or recommend models (that belongs to the Resource Router).
- Modify repository files or generate code.
- Load entire repositories into context.
- Read files outside the approved security perimeter.
- Guess conventions or patterns (it reads the project profile from memory).

## Inputs
- Active task description
- Workspace path
- Project Profile (from Memory Engine)
- List of open files in editor
- Active model context budget configuration

## Outputs
- Structured Context Package (JSON containing list of file paths, estimated tokens, and compressed signature payloads)
- Relevant file list for tool loading

## State
- Persistent State: None
- Temporary State: Current session file selection list, token usage metrics
- Cache: File signature cache (in memory) to prevent re-parsing unchanged files
- Configuration: Ignore glob patterns, file size compression limits
- Runtime Variables: Active workspace root, active model token limit

## Public API
- `Context.BuildPackage(task_desc, workspace_path, profile) -> ContextPackage`
- `Context.EstimateTokens(file_path) -> TokenCount`
- `Context.GetRelevantFiles(task_desc, profile) -> FileList`

## Script API (`src/context.py`)
- CLI: `python context.py --workspace <path> --task <task> --output json`
- Output: JSON Context Package details to stdout

## Event Subscriptions
- On TaskCreated
- On FileChange

## Events Published
- ContextReady(package)
- ContextBudgetExceeded(estimated, limit)
- ContextFailed(reason)

## Failure Conditions
- If estimated tokens exceed active model context budget:
  Publish ContextBudgetExceeded -> drop lowest relevance files from list -> re-calculate -> notify telemetry -> continue
- If selected file is binary or too large:
  Skip reading content -> extract file metadata only -> add warning payload -> continue
- If file reading permission error:
  Log error -> skip file -> add exclusion flag to Context Package -> continue

## Quality Standards
- Maximum execution latency: 200 ms
- Token estimation accuracy: Within ±10% of the host model's tokenizer
- Target context budget: Keep context under 20,000 tokens for simple/moderate tasks

## Security Rules
- Strictly validate all selected file paths against the workspace boundary.
- Scan file contents for secrets before packaging; redact any matched patterns.
- Never load files outside the active workspace.

## Recovery Strategy
Fallback to metadata-only context -> Exclude large files -> Request user to select files manually -> Log telemetry -> Abort

## Testing Strategy
- Unit Tests: Verify token estimation weights, regex secret scanner, glob ignore filtering.
- Integration Tests: Test context generation for a mock frontend component task.
- Performance Tests: Verify execution overhead remains below 200ms.

## Success Criteria
- Context Engine selects only the files that require modification or serve as dependencies.
- Token budget is respected without dropping critical dependency types.
- No secrets are passed in the final context package.
