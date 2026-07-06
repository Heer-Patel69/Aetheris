# Implementation Plan — Aetheris Engineering Kernel Specification (AEKS v1.0) Overhaul

Transition Aetheris into an **Engineering Hypervisor** that operates on an abstract, event-driven, decoupled capability architecture guided by the **Aetheris Engineering Kernel Specification (AEKS v1.0)**.

## Governance Standards & Constitution
- **Supreme Rule:** `LAW -1` (Aetheris is the source of engineering truth) and `LAW 0` (External frameworks are interchangeable capability modules).
- **Core Principle:** The kernel depends only on abstract capabilities via a centralized `CapabilityRegistry`. Providers like Headroom, ECC, and Claude Templates are resolved dynamically.
- **Event-Driven:** Engines communicate only by publishing/subscribing to events via the `EventBus`.

## Proposed Changes

### Component: Governance & Spec Documents
#### [MODIFY] [00_SYSTEM_CONSTITUTION.md](file:///c:/AI/Aehteris%20main/aetheris/00_SYSTEM_CONSTITUTION.md)
Update the constitution to formalize `LAW -1` and refactor `LAW 0` for the Engineering Hypervisor.

#### [NEW] [AEKS_v1.0.md](file:///c:/AI/Aehteris%20main/aetheris/docs/AEKS_v1.0.md)
The Aetheris Engineering Kernel Specification (AEKS v1.0) detailing the five domains, capability registry contracts, event schemas, graph connections, state directory structure, and Definition of Done.

#### [MODIFY] [ARCHITECTURE.md](file:///c:/AI/Aehteris%20main/aetheris/ARCHITECTURE.md)
Update diagrams and references to specify the 5 domains, capability registry, and event bus.

---

### Component: Core Domain (Lifecycle & State)
#### [MODIFY] [core.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/core.py)
Refactor `AetherisKernel` to handle user goals by coordinating the 5 domains via the `EventBus` and resolving capabilities dynamically.

#### [MODIFY] [event_bus.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/event_bus.py)
Enhance the `EventBus` to handle decoupling (publish/subscribe pattern for engines).

#### [MODIFY] [scheduler.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/scheduler.py)
Update to a parallel task scheduler that compiles a dependency task graph, executes batch queues, merges results, and triggers verification.

#### [NEW] [state.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/state.py)
Manage the `.aetheris/` directory state hierarchy structured like a git repository: config, state, memory, graphs, artifacts, etc.

---

### Component: Runtime Domain (Capability Registry & Providers)
#### [NEW] [base.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/providers/base.py)
Abstract capability base classes.

#### [NEW] [registry.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/providers/registry.py)
The `CapabilityRegistry` implementing dependency injection. Resolves capabilities (`compression`, `templates`, `hooks`, `embeddings`, `inference`) without referencing concrete provider classes.

#### [NEW] [headroom_provider.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/providers/headroom_provider.py)
Concrete provider for `compression` using headroom.

#### [NEW] [ecc_provider.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/providers/ecc_provider.py)
Concrete provider for `hooks` and `agents` using Everything Claude Code.

#### [NEW] [claude_template_provider.py](file:///c:/AI/Aehteris%20main/aetheris/src/kernel/providers/claude_template_provider.py)
Concrete provider for `templates` and `commands` using Claude Templates.

---

### Component: Intelligence Domain & Graph
#### [MODIFY] [ege.py](file:///c:/AI/Aehteris%20main/aetheris/src/intelligence/ege.py)
Upgrade the graph engine to support the unified **Engineering Intelligence Graph**:
`Business Graph -> Requirement Graph -> Product Graph -> Repository Graph -> Dependency Graph -> Technology Graph -> Architecture Graph -> Database Graph -> API Graph -> Security Graph -> Skill Graph -> RFC Graph -> SPEC Graph -> Execution Graph -> Benchmark Graph -> Decision Graph -> Memory Graph`

---

### Component: Verification & Policy Domains
#### [NEW] [policy.py](file:///c:/AI/Aehteris%20main/aetheris/src/validation/policy.py)
`PolicyEngine` validating all generated artifacts against rules (coding, architecture, security standards).

#### [NEW] [dod.py](file:///c:/AI/Aehteris%20main/aetheris/src/validation/dod.py)
`DoDEngine` enforcing phase validation: assertions that artifacts exist, verification/tests pass, logs/state are updated, and benchmarks are generated.

---

### Component: Tests
#### [NEW] [test_hypervisor.py](file:///c:/AI/Aehteris%20main/aetheris/tests/test_hypervisor.py)
Pytest verifying registry lookups, event dispatching, graph linkages, parallel scheduler batches, and DoD compliance.

---

## Verification Plan

### Automated Tests
- Run `python -m pytest tests/test_hypervisor.py` to assert correct implementation of registry mappings, provider isolation, event publishing, and graph traversal.
- Run the full suite `python -m pytest` to verify there are no regressions.
