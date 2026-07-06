# Aetheris Engineering Hypervisor — Architecture Reference

**Specification Version**: AEKS v1.0  
**Hypervisor Core Version**: 4.0.0  

---

## 1. System Overview

Aetheris operates as an **Engineering Hypervisor**. Instead of hardcoding engine references or third-party integrations, it is structured into **5 Domain Categories** coordinating via an asynchronous **Event Bus**. Third-party frameworks (Headroom, Everything Claude Code, Claude Code Templates) are resolved as abstract capabilities via a **Capability Registry**.

---

## 2. System Diagram

```text
                           USER GOAL
                               │
                               ▼
                AETHERIS ENGINEERING HYPERVISOR
                               │
       ┌───────────────────────┴───────────────────────┐
       │               Lifecycle Manager               │
       └───────────────────────┬───────────────────────┘
                               │
                               ▼
                       Workflow Scheduler
                               │
                               ▼
                      Capability Registry
                               │
    ┌───────────────┬──────────┴──────────┬───────────────┐
    ▼               ▼                     ▼               ▼
Core Domain    Intelligence Domain   Runtime Domain  Eng Domain
    │               │                     │               │
    └───────────────┼─────────────────────┼───────────────┘
                    ▼
          Capability Registry (DI) ➔ standard Interface
                    │
            ┌───────┼───────┐
            ▼       ▼       ▼
        Headroom   ECC   Templates
                    │
                    ▼
           Multi Model Router ➔ Gemini / Claude / GPT / GLM / Ollama
                    │
                    ▼
         Verification & Benchmarks
                    │
                    ▼
            .aetheris/ State Engine
```

---

## 3. The Five Architecture Domains

Aetheris classifies its engines under five logical namespaces:

| Domain | Purpose | Core Subsystems |
|---|---|---|
| **Core Domain** | Lifecycle orchestration, DAG schedulers, state storage checkpoints, policies, event bus | `KernelEngine`, `LifecycleEngine`, `WorkflowScheduler`, `StateEngine`, `PolicyEngine`, `EventBus` |
| **Intelligence Domain** | Code analysis, product parsing, context compilation, memory queries, performance metrics | `RepositoryIntel`, `ProductIntel`, `BusinessIntel`, `ArchitectureIntel`, `ContextCompiler`, `MemoryIntel`, `BenchmarkIntel` |
| **Engineering Domain** | Specialist domain validations (RFC/SPEC checks, DB migrations, API paths, tests, security) | `SkillEngine`, `RFCEngine`, `SPECEngine`, `DependencyEngine`, `APIEngine`, `DatabaseEngine`, `SecurityEngine`, `TestingEngine` |
| **Runtime Domain** | Sandbox executions, provider daemon managers, DI capability mapping, LLM routing, DoD engines | `ExecutionEngine`, `VerificationEngine`, `ArtifactEngine`, `ProviderManager`, `CapabilityRegistry`, `ModelRouter`, `DoDEngine` |
| **Infrastructure Domain** | Integrations, CLI CLI click command entries, dashboard visualization, and telemetry logs | `Marketplace`, `Dashboard`, `Telemetry`, `Analytics`, `CLI`, `Cloud`, `Extensions` |

---

## 4. Capability Registry & Providers

Capabilities are resolved dynamically. Concrete provider implementations inherit from base interfaces.

```text
                          Standard Interfaces
                     ┌─────────────┼─────────────┐
                     ▼             ▼             ▼
             HeadroomProvider  ECCProvider  ClaudeTemplateProvider
```

- **`compression`**: Handled by `HeadroomProvider` using SmartCrusher rules.
- **`hooks`**: Handled by `ECCProvider` utilizing Claude Code hooks.
- **`templates`**: Handled by `ClaudeTemplateProvider` loading Claude Templates.

---

## 5. State Ownership Map (`.aetheris/`)

The hypervisor state is tracked under the `.aetheris/` directory matching the layout specified in [AEKS v1.0](docs/AEKS_v1.0.md).

---

## 6. Execution Pipeline

```text
Goal Received ➔ Index Repository ➔ Resolve Capabilities ➔ Build Task Graph ➔ Execute Batches (Parallel) ➔ Validate DoD ➔ Commit State
```
Communication is completely decoupled. Nothing calls another engine directly; everything communicates via the `EventBus`:

```text
GoalReceived ➔ RepositoryIndexed ➔ CapabilityResolved ➔ TaskScheduled ➔ VerificationPassed ➔ StateSaved
```