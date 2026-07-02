# ADR-008: Version Contract

## Status
APPROVED

## Context
As the Aetheris Kernel runtime evolves, changes to configuration formats, memory schemas, and script contracts can introduce bugs if versions mismatch. We need a clear contract for how versions are defined, validated, and managed across the runtime components.

## Decision
We enforce a strict versioning policy based on **Semantic Versioning 2.0.0 (SemVer)**:

1. **Master Version**:
   - The master version is defined in a single file: `aetheris/VERSION` (currently `2.0.0`).
   - Every skill `SKILL.md` must declare this version in its frontmatter metadata block:
     ```yaml
     metadata:
       version: v2
       patch: 2.0.0
     ```

2. **State & Cache Schema Versioning**:
   - All persisted state files (e.g., `project-profile.yaml`, `decisions.jsonl`) must include a `schema_version` field.
   - The Memory Engine MUST validate the `schema_version` when loading state.
   - If a major version mismatch is detected (e.g., loading a v1.0 profile into a v2.0 runtime), the Memory Engine must not load the data. Instead, it must trigger re-discovery to overwrite the old profile.

3. **Validation & Doctor Checks**:
   - The `doctor.py` utility verifies version consistency across:
     - All installed global skills
     - The installed scripts
     - The loaded configuration files
   - Any version mismatch flags a warning and recommends running `python install.py update` to sync components.

## Consequences
- Prevents runtime errors caused by mismatched skill instructions and Python script logic.
- Avoids silent state corruption from legacy format caches.
- Clear update paths for developers and users.

## Alternatives Considered
- **Unversioned/Rolling System**: Relying on git commit hashes. *Rejected* because commit hashes do not convey compatibility or API stability, and are not easily parsed by verification logic.
- **Per-module Versioning**: Allowing each module to version independently (e.g., Kernel v2.0, Router v1.4). *Rejected* because it increases maintenance overhead significantly and complicates compatibility matrix mapping.