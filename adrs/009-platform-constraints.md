# ADR-009: Platform Constraints

## Status
APPROVED

## Context
Antigravity is a sandboxed developer tool that runs outside of the editor's core process space. It does not provide hooks for intercepting requests, programmatically switching model providers, or direct access to billing telemetry. We must explicitly document these limitations and establish the architectural workarounds to make the runtime functional.

## Decision
We identify and work around four key platform constraints:

### 1. No Programmatic Model Selection
- **Constraint**: The host environment decides which model is running; our code cannot force a model switch.
- **Workaround**: The LLM Router acts as an **advisory** module. It calculates the optimal model and outputs it to the pipeline trace. The active model then reads its own configuration from `models.yaml` and adapts its response style, context depth, and cost strategies to match its actual active capabilities.

### 2. No Request Interception Hooks
- **Constraint**: Antigravity does not run a daemon that intercepts every user prompt before the model reads it.
- **Workaround**: We use two hooks:
  - A global rules file `~/.gemini/config/AGENTS.md` which instructs the model to check if `univoid-brain-kernel` is present and follow its pipeline loop.
  - The Kernel instruction set, which forces the LLM to process every input through the 8 stages sequentially.

### 3. No Direct Token or Cost Metering
- **Constraint**: The active model has no API access to count tokens in real-time or retrieve billing data.
- **Workaround**: The Cost Optimizer uses standard token-estimation heuristics (e.g., character count / 4 for English text, regex scanners for code blocks) and multiplies them by the pricing listed in `costs.yaml`.

### 4. No Background Process Daemon
- **Constraint**: Python scripts cannot run persistently; they are executed on-demand and must terminate quickly.
- **Workaround**: The runtime is stateless. State is persisted in JSON/YAML files on disk. Every script invocation reads the state, performs its task, writes the updated state, and exits.

## Consequences
- The runtime operates safely within the sandboxed boundaries of Antigravity.
- Users are notified of optimal model configurations without breaking the host application's settings.
- If Antigravity adds native hooks in a future update, we can replace these workarounds without rewriting the core kernel logic.

## Alternatives Considered
- **Custom Wrapper Executable**: Shipping a custom CLI wrapper that intercept prompts before calling Gemini. *Rejected* because the user interacts directly through the Antigravity IDE, and forcing the user to use a custom CLI defeats the integration goal.
