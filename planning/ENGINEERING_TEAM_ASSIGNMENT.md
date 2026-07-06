# Engineering Team Assignment: Aetheris Engineering Kernel Specification (AEKS v1.0) Overhaul

This document assigns roles, skills, and specification domains for restructuring the Aetheris Kernel into an Engineering Hypervisor matching the AEKS v1.0 specification.

## Roles & Assignments

| Role | Mapped Skills | Governing Specification | Responsibility |
|---|---|---|---|
| **Product Manager** | `aetheris-product-intelligence` | AEKS Core Domain | Define the AEKS v1.0 specifications, 5 Domains (Core, Intelligence, Engineering, Runtime, Infrastructure), and DoD Engine criteria. |
| **Solution Architect** | `agency-software-architect` | AEKS Runtime Domain | Design the Dependency Injection (DI) Capability Registry, Provider Layer, Event Bus architecture, and the connected 17-subgraph Engineering Intelligence Graph. |
| **Engineering Lead** | `agency-senior-developer` | AEKS Core & Engineering Domains | Restructure the core loop into an event-driven flow, build the parallel task graph scheduler, and implement the five domain engine registries. |
| **Backend & Integration Engineer** | `agency-backend-architect` | AEKS Runtime Domain | Code the Capability Registry, abstract interfaces for `compression`, `templates`, and `hooks` capabilities, and wrap their respective providers. |
| **QA / Verification Engineer** | `aetheris-verification-engine` | AEKS Runtime Domain | Build the Definition of Done (DoD) engine, Policy engine validator, and write test suites asserting decoupled capabilities, events, and graph linkages. |
| **Technical Writer** | `agency-technical-writer` | AEKS Infrastructure Domain | Create `docs/AEKS_v1.0.md` (renamed from Global Operating Policy), update the system constitution, architecture manuals, and README. |

## Department Mobilization

- **Core / Scheduler**: Re-architecting the task graph builder, workflow scheduler, state checkpoints, and event bus.
- **Intelligence**: Enhancing repository, product, business, context, memory, and benchmark intelligence engines.
- **Engineering / Domain Controllers**: Structuring skills, RFC/SPEC validation, database, API, security, testing, and deployment.
- **Runtime / Provider Sandbox**: Setting up the capability registry (ECC/Headroom/Templates decoupling) and the DoD verification engine.
- **Infrastructure**: Telemetry, dashboard visualization, and CLI updates.
