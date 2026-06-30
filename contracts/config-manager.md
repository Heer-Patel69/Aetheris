# Module: Configuration Manager

## Header
- Name: Configuration Manager
- Version: 2.1.0
- Purpose: Load, merge, and validate system and workspace configuration files.
- Owner: Configuration Manager
- Dependencies: None (all other modules depend on Configuration Manager)
- Security Level: HIGH
- Performance Target: Config loading and schema validation completed in <50ms.

## Mission
The Configuration Manager exists solely to parse, deep-merge, and schema-validate system configurations. It is forbidden from executing business logic or holding runtime session state.

## Responsibilities
- Load configuration files across the 4-tier hierarchy: Shipped Defaults, User Global Overrides, Project Local Overrides, and Runtime Overrides.
- Perform deep-recursive merging of configuration dictionaries.
- Validate the merged configuration against defined JSON Schemas.
- Prevent credential leaking by validating that no secrets exist in repository-committed files.
- Provide a clean Public API for other modules to request configurations.

## Explicitly Forbidden
The Configuration Manager MUST NOT:
- Write configuration overrides to disk (it is a read-only configuration loader).
- Read `.env` files or execute credential-bearing scripts (that belongs to the Security review boundary).
- Reason about model choices or specialist routing.
- Execute shell commands or run tool pipelines.
- Store runtime session state.

## Inputs
- Default config files: `aetheris/config/*.yaml`
- User global config folder: `~/.aetheris/config/*.yaml`
- Project config folder: `<workspace>/.aetheris/config/*.yaml`
- Runtime overrides passed via command-line options
- Config schemas: `aetheris/schemas/*.schema.json`

## Outputs
- Validated, merged configuration object (JSON/dictionary)
- Validation error records (if schema validation fails)

## State
- Persistent State: None (stateless across cycles)
- Temporary State: Loaded file contents and merged settings
- Cache: In-memory cache of validated configurations to prevent multiple disk reads in the same execution cycle
- Configuration: Configuration file paths
- Runtime Variables: Active workspace path

## Public API
- `Config.LoadAll(workspace_path, runtime_overrides) -> MergedConfig`
- `Config.GetSection(section_name) -> ConfigDictionary`
- `Config.ValidateSchema(config_data, schema_name) -> ValidationResult`

## Internal API
- `_deepMerge(dict_a, dict_b) -> MergedDict`
- `_loadYamlFile(file_path) -> Dictionary`
- `_checkForSecrets(dictionary) -> bool`

## Event Subscriptions
- On ConfigChanged

## Events Published
- ConfigLoaded(version)
- ConfigValidationError(errors)

## Failure Conditions
- If config file corrupted or invalid YAML:
  Delete corrupted workspace config file -> notify telemetry -> fallback to global defaults -> continue
- If schema validation fails:
  Publish ConfigValidationError -> fallback to default configuration -> notify telemetry -> continue
- If secret detected in project config:
  Reject loading project-level configuration -> fall back to user config -> notify telemetry -> print security alert to stderr

## Quality Standards
- Maximum latency: 50 ms
- Maximum memory: 50 MB
- Minimum schema validation accuracy: 100%
- Configuration loading must be idempotent

## Security Rules
- Never read credentials or secrets.
- Never write configurations back to the repository.
- Verify file permissions of configuration directories before reading.
- Fail closed if a secret is found in a project-level config file.

## Recovery Strategy
Retry load -> Fallback to global user overrides -> Fallback to shipped defaults -> Abort with error message

## Testing Strategy
- Unit Tests: Validate deep merge logic, yaml parser, secret scanner.
- Integration Tests: Test merging of Tiers 1-4, test invalid file formats.
- Stress Tests: Merge 1,000 deep keys, test parsing large YAML config files.
- Security Tests: Inject mocked API keys into project config and verify they are rejected.

## Success Criteria
- Config manager loads all configurations in under 50ms.
- Schema validation correctly catches invalid keys.
- Merged config contains correct overrides from project local settings.