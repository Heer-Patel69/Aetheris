# ADR-001: Module Boundaries

## Status
APPROVED

## Context
The Aetheris Kernel runtime needs to be highly modular to prevent context window exhaustion and ensure maintainability. We need to clearly define the boundaries of a "module" and establish rules for when logic belongs in the LLM instruction layer (Skills/References) versus the execution layer (Python scripts).

## Decision
We establish a strict tripartite architectural structure for every module:
1. **Instruction Layer (Antigravity Skill `SKILL.md`)**: Contains the high-level identity, core mission, constraints, and the dispatcher logic for the LLM. It defines what the module is and what it must not do.
2. **Context Layer (References `references/*.md`)**: Contains deep details, checklists, priority matrices, and specifications that are only read on-demand via the `view_file` tool.
3. **Execution Layer (Python Scripts `src/` installed to `scripts/`)**: Contains all programmatic logic, side effects, filesystem access, calculations, and structured data handling.

### Rules of Separation
- **No file system manipulation in markdown**: Skills and references must never instruct the LLM to perform ad-hoc file operations. They must instead instruct the LLM to invoke the module's corresponding Python script (e.g., `python scripts/scanner.py`).
- **No reasoning in scripts**: Python scripts must not attempt to reason about user intent, architect solutions, or make qualitative decisions. They are input-output machines that process data, query files, and return structured JSON/YAML.
- **On-demand loading**: Reference documents must be kept small (under 8KB each) and focused on a single topic. The LLM must only read them when explicitly entering that specific pipeline stage.

## Consequences
- **Context Preservation**: The LLM's context window is protected from bloat because massive rulesets and indices are relegated to scripts or reference files that are only loaded when active.
- **Programmatic Reliability**: Operations like filesystem scanning and state caching are executed deterministically by Python, avoiding LLM inaccuracies.
- **Symmetrical Testability**: Python scripts can be tested using standard pytest suites, while skill files are tested via mock conversation frameworks.

## Alternatives Considered
- **Pure Prompt Model**: Discarding scripts and handling all state/discovery via LLM instructions. *Rejected* because LLMs cannot perform reliable, deep directory scanning or maintain deterministic state caches on Windows filesystems without hallucination or truncation.
- **Pure Python Wrapper**: Running a wrapper script that calls the Gemini API directly. *Rejected* because Antigravity is the host environment, and we must operate within its skill/command orchestration boundaries.