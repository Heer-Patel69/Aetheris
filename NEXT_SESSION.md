# UniVoid Brain OS — Next Session Steps

**Version**: 2.0.0
**Target Phase**: Phase 2 — Module Contracts

## Objective

In the next session, you must specify the formal **Module Contracts** for all 12 modules defined in the System Constitution. No implementation code is to be written during this phase.

---

## Prerequisites

Read the following files from the repository root to recover full context:
1. [00_SYSTEM_CONSTITUTION.md](file:///c:/AI/Agency%20owner/brain-os/00_SYSTEM_CONSTITUTION.md) — The supreme governing design philosophy and constraints.
2. [PROJECT_STATE.md](file:///c:/AI/Agency%20owner/brain-os/PROJECT_STATE.md) — The active tracker showing Phase status.
3. [DECISIONS.md](file:///c:/AI/Agency%20owner/brain-os/DECISIONS.md) — Approved D-001 through D-010 decisions and ADRs 001-010.
4. All files in the [adrs/](file:///c:/AI/Agency%20owner/brain-os/adrs) folder.

---

## Action Plan — Phase 2: Module Contracts

You must generate 12 markdown files under `brain-os/contracts/`.

### 1. Contract Template

Every module contract MUST follow this exact structure without omission (see the Kernel Contract in [implementation_plan.md](file:///C:/Users/heerp/.gemini/antigravity-ide/brain/1a2fb65f-e7f6-4b3e-b8c4-ab6fc81631a1/implementation_plan.md) as a reference specimen):

```markdown
# Module: [Name]

## Header
- Name:
- Version: 2.0.0
- Purpose:
- Owner:
- Dependencies:
- Security Level:
- Performance Target:

## Mission
Exactly one sentence defining its sole purpose.

## Responsibilities
What the module MUST do.

## Explicitly Forbidden
What the module MUST NEVER do.

## Inputs
Types, sources, constraints.

## Outputs
Types, consumers, guarantees.

## State
Persistent, Temporary, Cache, Config, Runtime variables.

## Public API
Signature, params, return types.

## Internal API
Private operations.

## Event Subscriptions
Events it listens to.

## Events Published
Events it publishes.

## Failure Conditions
Deterministic recovery chains: If [condition] -> [action]

## Quality Standards
Latency, memory, token, confidence limits.

## Security Rules
Mandatory access controls.

## Recovery Strategy
Ordered fallback chain.

## Testing Strategy
Unit, integration, stress, security coverage.

## Success Criteria
What verifies correct operation.
```

### 2. Execution Order

Write the 12 contracts in this sequence. Review each against the System Constitution before proceeding:

1. `brain-os/contracts/config-manager.md`
2. `brain-os/contracts/telemetry-engine.md`
3. `brain-os/contracts/memory-engine.md`
4. `brain-os/contracts/project-discovery.md`
5. `brain-os/contracts/context-engine.md`
6. `brain-os/contracts/planner.md`
7. `brain-os/contracts/llm-router.md`
8. `brain-os/contracts/specialist-router.md`
9. `brain-os/contracts/cost-optimizer.md`
10. `brain-os/contracts/verification-engine.md`
11. `brain-os/contracts/plugin-manager.md`
12. `brain-os/contracts/kernel.md` (LAST)

### 3. Verification

Once all 12 contracts are written:
1. Update `PROJECT_STATE.md`: mark Phase 2 as complete, Phase 3 as next.
2. Stop and request user review.
