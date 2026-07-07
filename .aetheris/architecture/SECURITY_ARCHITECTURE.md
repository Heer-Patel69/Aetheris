# Aetheris Security & Sandboxing Specification

## 1. Threat Model & Overview
Aetheris executes arbitrary LLM-generated code and runs third-party integrations (Headroom, ECC, OpenHands). This presents extreme security risks, including arbitrary remote code execution (RCE), prompt injection, and host escape.

## 2. Prompt Injection Defense
- **The EDO Filter**: The Executive Decision Orchestrator must run a preliminary semantic scan on all user inputs to detect "ignore previous instructions" or "bypass planning" attempts.
- **Immutable System Prompt**: The Aetheris Constitution and Kernel Rules are injected directly into the API context at runtime and cannot be overridden by user input.

## 3. Runtime Sandboxing (ROE)
The Runtime Orchestrator Engine (ROE) is responsible for executing the selected skills and code.
- **Containerization**: All python executions must run inside isolated Docker containers or strict PySandbox environments.
- **Network Isolation**: The execution container must not have outbound internet access unless explicitly granted by the Capability Resolution Engine (CRE).
- **File System Jails**: Skills can only read/write to the designated `workspace/` directory.

## 4. Data Privacy & Secrets
- **Secret Manager**: API keys (OpenAI, Anthropic, Vector DB auth) are stored in encrypted `config/.env` and injected dynamically into the runtime adapter. They are never logged.
- **Observability Redaction**: The Observability Engine (OE) must scrub all prompt payloads of PII or API tokens before writing traces.

## 5. Acceptance Criteria
- Running `os.system("rm -rf /")` via a dynamically generated skill must fail with a `PermissionError`.
- No LLM prompt payload can ever overwrite the `AEOS_GLOBAL_OPERATING_POLICY`.
