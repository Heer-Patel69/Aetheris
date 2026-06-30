# ADR-007: Script Execution Model

## Status
APPROVED

## Context
Antigravity executes external tools via the `run_command` interface. Since our runtime consists of several Python scripts that manipulate the filesystem, calculate hashes, and manage configuration, we need a standard contract for how these scripts are invoked, how they receive inputs, and how they return outputs to the LLM.

## Decision
We establish the following standard contract for all executable Python scripts in the runtime:

1. **Invocation Path**:
   - All scripts are located in the `src/` directory of the repository and built/installed to the global skill's `scripts/` directory.
   - The LLM invokes them using the `run_command` tool.
   - Example invocation command line:
     ```powershell
     python "C:\Users\heerp\.gemini\config\skills\univoid-project-discovery\scripts\scanner.py" --workspace "c:\AI\Agency owner"
     ```

2. **Input Contract**:
   - Arguments must be passed as explicit command line flags (e.g., `--workspace <path>`).
   - For complex, nested data inputs (such as saving project profile metadata), the script must accept JSON input via a `--data` flag or through standard input (`stdin`).

3. **Output Contract**:
   - All scripts must output their results to standard output (`stdout`) as a single, formatted JSON block. No plain text logging is allowed on `stdout`.
   - Logging, progress bars, and debugging info must be written to standard error (`stderr`) or logged directly to the telemetry file path.
   - The exit code of a successful script execution must be `0`. Any non-zero exit code represents a execution failure.

## Consequences
- The LLM/Kernel can cleanly parse script results using simple regex or JSON parser tools.
- Terminal output noise is minimized, preventing context pollution.
- Stderr outputs are separated, making errors easy to detect.

## Alternatives Considered
- **Standard Text Outputs**: Outputting human-readable text tables. *Rejected* because text structures are difficult for the LLM/Kernel to parse reliably, leading to regex matching failures.
- **IPC over WebSockets**: Keeping a Python process running in the background and communicating via WebSockets. *Rejected* because Antigravity does not support background services, and running an unmanaged background process violates security policy.
