# Aetheris Engineering Kernel Specification (AEKS v1.0)

**Version:** 1.0.0  
**Status:** Approved Specification  
**Authority:** Supreme architectural directive for the Aetheris Engineering Hypervisor  

---

## 1. Core Principles

Aetheris is an **Engineering Hypervisor**. It orchestrates the lifecycle, state, planning, verification, and intelligence of software engineering, treating external frameworks strictly as interchangeable capability modules.

### LAW -1: Authority of Truth
Aetheris is always the source of engineering truth. External systems may provide compression, templates, agents, hooks, prompts, commands, or execution, but they must never replace Aetheris' Repository Intelligence, Product Intelligence, Engineering Intelligence, Planning, Verification, Memory, or Engineering Lifecycle. The Kernel always owns the final decision.

### LAW 0: Framework Subordination
Every external framework—including Headroom, Everything Claude Code, Claude Code Templates, MCP Servers, RAG Engines, Compression Engines, Agent Frameworks, Prompt Libraries, and Model SDKs—is an implementation module. None are allowed to control the engineering workflow. Only the Aetheris Kernel controls the lifecycle.

---

## 2. System Architecture Domains

The engines of Aetheris are grouped into five distinct domains:

### 1. Core Domain (Lifecycle & Coordination)
- **Kernel Engine:** Manages lifecycle bootstrap and loop execution.
- **Lifecycle Engine:** Controls system state transitions across the pipeline.
- **Workflow Scheduler:** Compiles and executes task dependency graphs.
- **State Engine:** Persists the system state and manages structural checkpoints.
- **Policy Engine:** Validates artifacts against enterprise-wide rules and guidelines.
- **Event Bus:** Provides asynchronous, decoupled communication channels for all engines.

### 2. Intelligence Domain (Reasoning)
- **Repository Intelligence:** Models code semantics and index maps.
- **Product Intelligence:** Understands requirements and builds features list.
- **Business Intelligence:** Maps target personas and business model contexts.
- **Architecture Intelligence:** Recommends framework stacks and modular separations.
- **Planning Intelligence:** Decides execution strategy blueprints.
- **Context Compiler:** Collects and bundles minimal, rich context packages.
- **Memory Intelligence:** Manages semantic, episodic, and procedural cache.
- **Benchmark Intelligence:** Measures performance and token efficiency.

### 3. Engineering Domain (Subsystem Modeling)
- **Skill Engine:** Scrapes and manages specialist capability tools.
- **RFC Engine:** Inspects requested designs against design document criteria.
- **SPEC Engine:** Audits codebase against technical specifications contracts.
- **Dependency Engine:** Analyzes package dependency matrices and version rules.
- **API Engine:** Inspects routes, payloads, and OpenAPI documentation schema.
- **Database Engine:** Validates migrations, schemas, index constraints.
- **Security Engine:** Scans OWASP vulnerabilities and credential leakage.
- **Testing Engine:** Validates unit, integration, and E2E test coverage.
- **Deployment Engine:** Inspects Dockerfiles, CI/CD pipeline manifests.

### 4. Runtime Domain (Execution Layer)
- **Execution Engine:** Runs the scheduled batches inside target environments.
- **Verification Engine:** Compiles validation summaries for each step.
- **Artifact Engine:** Registers and version-controls all compiled assets.
- **Provider Manager:** Controls start, stop, and status monitoring of provider daemons.
- **Capability Registry:** Standardizes interfaces mapping abstract capability tags to providers.
- **Plugin Manager:** Registers extensions and hook callbacks.
- **Model Router:** Classifies task requirements to select the optimal LLM.

### 5. Infrastructure Domain (Integration)
- **Marketplace:** Discovers external plugins and provider bundles.
- **Dashboard:** Exposes live visual status views.
- **Telemetry:** Collects runtime metrics and prints logs.
- **Analytics:** Compiles trends over execution history.
- **CLI:** Command-line entry points.
- **Cloud:** Cloud sync and remote backups.
- **Extensions:** Code editor plugins.

---

## 3. Capability Registry & Providers

The Kernel never interacts directly with third-party tools. Instead, it queries the `CapabilityRegistry` to resolve abstract capability keys:

```text
Kernel/Engines ➔ CapabilityRegistry ➔ base Interface ➔ Provider Wrapper ➔ Subsystem Command
```

### Standard Capability Mappings
1. **`compression`:** Mapped to `HeadroomProvider` using the SmartCrusher context policies.
2. **`templates`:** Mapped to `ClaudeTemplateProvider` to translate CLI commands and macros.
3. **`hooks`:** Mapped to `ECCProvider` to execute isolated environment hooks and sub-agents.
4. **`embeddings`:** Resolved to OpenAI, Gemini, or Local Embedding endpoints.
5. **`inference`:** Resolved by the Model Router to Gemini, Claude, GPT, GLM, or local models.

---

## 4. Event Bus Specification

Engines are entirely decoupled. They must communicate exclusively via events published to the `EventBus`.

### Core Event Triggers
- `GoalReceived`: Triggered when the user enters an engineering goal.
- `RepositoryIndexed`: Triggered when Repository Intelligence finishes a sweep.
- `CapabilityResolved`: Triggered when a requested capability is resolved from the registry.
- `ContextCompiled`: Triggered when Context Compiler finishes building context.
- `CompressionFinished`: Triggered when the compression provider finishes processing.
- `TaskScheduled`: Triggered when Workflow Scheduler schedules task graph nodes.
- `VerificationFailed`: Triggered when Verification Engine finds an issue.
- `DeploymentFinished`: Triggered when Deployment Engine finishes deploying.
- `StateSaved`: Triggered when State Engine saves checkpoints.

---

## 5. Engineering Intelligence Graph

Aetheris maps the repository and execution state into a connected Engineering Intelligence Graph containing 17 subgraphs:

```text
Business Graph ➔ Requirement Graph ➔ Product Graph ➔ Repository Graph ➔ Dependency Graph
➔ Technology Graph ➔ Architecture Graph ➔ Database Graph ➔ API Graph ➔ Security Graph
➔ Skill Graph ➔ RFC Graph ➔ SPEC Graph ➔ Execution Graph ➔ Benchmark Graph ➔ Decision Graph
➔ Memory Graph
```

---

## 6. Git-like State Management (`.aetheris/`)

The state of the hypervisor is maintained under the `.aetheris/` directory matching the following layout:

```text
.aetheris/
├── config/       # Global/local workspace yaml overrides
├── state/        # Execution states, PIDs, active phase JSONs
├── memory/       # Episodic/semantic memory files
├── graphs/       # engineering.graph.json, sub-graphs
├── artifacts/    # Version-controlled specs, blueprints, and files
├── logs/         # telemetries, command logs
├── providers/    # Provider configurations
├── skills/       # Custom execution skills
├── rfcs/         # Governance RFCs
├── specs/        # Subsystem SPEC contracts
├── benchmarks/   # Telemetry metrics and stats
├── analytics/    # Historical trend graphs
├── history/      # Full CLI execution history
├── snapshots/    # File tree recovery snapshots
├── cache/        # Intermediate compiler caches
├── checkpoints/  # Workflow scheduler rollbacks
└── reports/      # DoD reports, traceability matrixes
```

---

## 7. Definition of Done (DoD) Checklist

No stage execution or task is marked complete unless the `DoDEngine` asserts:
1. **Artifacts Exist:** All expected output files are present.
2. **Verification Passed:** Verification checks report zero errors.
3. **Tests Passed:** Test suites run successfully (100% pass).
4. **Logs Updated:** Execution logs and state metadata are saved.
5. **.aetheris Updated:** State, graphs, and snapshots are updated.
6. **Benchmarks Generated:** Token and performance metrics are logged.
7. **Traceability Updated:** Traceability matrix maps back to requirements.
