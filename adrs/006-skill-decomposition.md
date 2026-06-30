# ADR-006: Skill Decomposition

## Status
APPROVED

## Context
Antigravity discovers and registers instructions from files located in `~/.gemini/config/skills/`. If we bundle the entire Aetheris Kernel runtime into a single skill, the LLM must load all 34KB of instructions on every invocation, causing context bloat and increasing the likelihood of instructions overriding each other. We need to decide how to decompose the runtime into Antigravity's skill structure.

## Decision
We decompose the 12-component architecture into **8 distinct, global Antigravity skills**:

1. **`aetheris-kernel`**: Coordinates the pipeline (INGEST, EXECUTE, COMMIT, LOG).
2. **`aetheris-project-discovery`**: Orchestrates repository scanning.
3. **`aetheris-skill-orchestrator`**: Handles model selection and specialist routing.
4. **`aetheris-verification-engine`**: Manages CTO/CSO/QA quality gates.
5. **`aetheris-context-engine`**: Selects and compresses context.
6. **`aetheris-memory-engine`**: Persists profiles and decisions.
7. **`aetheris-product-intelligence`**: Handles task decomposition and scheduling.
8. **`aetheris-cost-optimizer`**: Evaluates model pricing and token limits.

*Note: Telemetry, Provider Manager, and Config Manager operate as pure Python scripts called by the skills above; they do not have separate LLM skill interfaces.*

### Trigger Matching Strategy
- Each skill file `SKILL.md` declares its name and description in YAML frontmatter.
- The description is optimized to trigger-match specific keywords. For example, `aetheris-project-discovery` triggers on "scan project", "read stack", "determine repository conventions".
- Once triggered, the skill relies on its `references/*.md` files for stage-specific checklists, loading them only when the Kernel dispatches that stage.

## Consequences
- **Context Economy**: The LLM only loads instructions for active stages (e.g., loading verification rules only during the VERIFY stage).
- **Loose Coupling**: If the verification logic changes, only `aetheris-verification-engine` needs to be rebuilt, leaving the Kernel and Discovery skills untouched.
- **Trigger Integrity**: By using descriptive prefixes and trigger terms, we prevent namespace collisions with user-written skills.

## Alternatives Considered
- **Single Monolithic Skill (`aetheris-brain-os`)**: Bundle all references and stages under one directory. *Rejected* because the LLM is forced to digest all module rules simultaneously, leading to instruction neglect and context window waste.
- **Project-scoped Rules (`.agents/` or `AGENTS.md`)**: Putting the runtime in workspace files. *Rejected* because the runtime must remain global and work out-of-the-box on new empty workspaces.