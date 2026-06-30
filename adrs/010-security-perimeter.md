# ADR-010: Security Perimeter

## Status
APPROVED

## Context
AI runtimes require significant execution authority (running filesystem tools, creating configuration files, executing scripts). Without a strictly defined security perimeter, the runtime could accidentally read credentials, modify git history, delete user files, or execute malicious external commands.

## Decision
We enforce a strict **Security Perimeter** for all modules, scripts, and skills:

1. **Path Read/Write Restrictions**:
   - **Allowed Read Areas**:
     - The active workspace directory (recursive).
     - The global configurations folder (`~/.gemini/config/`).
     - The global state directory (`~/.aetheris/`).
   - **Allowed Write Areas**:
     - The project state folder (`<workspace>/.aetheris/`).
     - The global state folder (`~/.aetheris/`).
     - The global skill installation folder (`~/.gemini/config/skills/aetheris-*/`) during installation/updates only.
   - **Forbidden Areas**: All other paths are strictly off-limits. No reading home directories, system temporary files, or other repositories.

2. **Secret Separation Invariant**:
   - The runtime (scripts and LLM instructions) is **explicitly forbidden** from reading files named `.env`, `.env.local`, or any file containing active credentials.
   - If a script encounters a file containing keys or tokens during workspace scanning, it must redact those keys before outputting the JSON profile.

3. **Execution Restrictions**:
   - The runtime must only execute Python scripts located within the installed skill directories.
   - Arbitrary binaries, shell commands (e.g., `rm -rf`, `curl`, `wget`), or unverified packages must never be run without explicit user review.

4. **Deletion Protection**:
   - The runtime must never delete, prune, or truncate files in the user's codebase. It may only write file modifications as git-staged changes or diff patches, leaving the final git commit to the user.

## Consequences
- Prevents accidental data loss or security leaks in high-risk projects.
- Keeps config keys separate from committed workspace settings.
- The runtime passes security checks for corporate development workspaces.

## Alternatives Considered
- **Docker Isolation**: Running all Python scripts in a Docker container. *Rejected* because of the excessive performance overhead, requirement of having Docker running on the host system, and the fact that path restrictions in Python are sufficient for this sandbox level.