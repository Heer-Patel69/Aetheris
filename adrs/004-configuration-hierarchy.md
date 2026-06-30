# ADR-004: Configuration Hierarchy

## Status
APPROVED

## Context
The Brain OS runtime must work out-of-the-box on new empty directories, but it must also allow users to customize their preferences globally (across all projects) and override settings for specific repositories (such as strictness of verification gates or specialist teams). We need a clear, deterministic hierarchy for configuration merging.

## Decision
We implement a **4-tier Configuration Hierarchy** managed by the **Configuration Manager**:

1. **Hierarchy Order (Lowest to Highest Priority)**:
   - **Tier 1: Defaults** (Source Code): Hardcoded defaults in `config.py`.
   - **Tier 2: Shipped Defaults** (`brain-os/config/*.yaml`): Installed config files representing out-of-the-box defaults.
   - **Tier 3: User Global Overrides** (`~/.univoid/brain/config/*.yaml`): Global user preferences, provider keys/selections, and custom thresholds.
   - **Tier 4: Project Local Overrides** (`<workspace>/.univoid/config/*.yaml`): Project-specific settings (e.g., locking specific models or disabling certain specialist categories).
   - **Tier 5: Runtime Overrides** (Command arguments or session parameters): Highest priority, valid for the current pipeline turn only.

2. **Merge Mechanics**:
   - The Config Manager (`src/config.py`) loads Tiers 1–4 sequentially.
   - Values are merged deep-recursively. For dictionaries, Tier N overrides keys in Tier N-1. For lists, Tier N completely replaces the list in Tier N-1 (lists are never appended or merged).
   - Schema validation is performed on the final merged object before any config is returned. If validation fails, the Config Manager logs a validation error and falls back to Tier 2 (Shipped Defaults).

3. **Secret Separation**:
   - No API keys or credential variables are allowed in Tier 2 or Tier 4.
   - Project configurations (`.univoid/config/`) must be commit-safe. All provider secrets must be loaded via local environment variables or referenced from Tier 3 (Global User Overrides).

## Consequences
- The user can configure settings once globally, and they will persist across all workspaces.
- Teams can commit `.univoid/config/` to their git repositories to enforce uniform coding standards or specialist routing rules without sharing API keys.
- If a project config contains invalid YAML, the system safely falls back to global settings, preserving runtime stability.

## Alternatives Considered
- **Environment Variables Only**: Relying solely on env vars for project-specific customization. *Rejected* because env vars are hard to version control, cannot easily express complex nested objects (like specialist scoring weights), and pollute the shell namespace.
- **Single Monolithic Configuration**: Combining all configs (models, specialists, costs) into one file. *Rejected* because separating them (e.g., `models.yaml`, `specialists.yaml`) allows modules to load only the specific config block they require, minimizing disk reading.
