# Test Plan: Configuration Manager

## 1. Scope
This test plan covers the verification of loading, merging, and schema-validating configurations across Tiers 1–4.

## 2. Test Cases

### 2.1 — Successful Merge (Pass)
- **Condition**: Load configurations from default, user overrides, and project overrides.
- **Expected Outcome**: Settings are deep-merged correctly. Values in higher tiers successfully override values in lower tiers (e.g. project setting overrides user setting). Output conforms to `brain.schema.json`.

### 2.2 — Schema Validation Failure (Fail)
- **Condition**: Inject an invalid value (e.g. `timeouts.execute = "invalid_string"` or `limits.max_retries_per_task = 10` which is above maximum limit).
- **Expected Outcome**: Configuration validation fails, Config Manager emits a `ConfigValidationError` event, falls back to default settings, and pipeline continues with warning.

### 2.3 — Secrets Scanning Block (Fail)
- **Condition**: Inject a mock API key (e.g. `supabase_key = "sb_key_1a2b3c4d5e"`) inside project-level configuration `brain.yaml`.
- **Expected Outcome**: Configuration Manager rejects the project config file, falls back to global user settings, logs a security violation, and continues.

### 2.4 — Missing Configuration File (Edge Case)
- **Condition**: Load configurations when project override `brain.yaml` is missing.
- **Expected Outcome**: Loads default settings and global overrides gracefully without throwing file-not-found errors.

## 3. Performance Benchmarks
- Configuration loading, merging, and schema validation MUST complete in **<50ms**.
- Configuration validation on empty configurations must complete in **<10ms**.

## 4. Security Validation Scenarios
- Attempt to inject file system paths containing directory traversal patterns in configuration paths and verify they are rejected.
- Verify that no secrets, tokens, or credential-like strings pass validation.