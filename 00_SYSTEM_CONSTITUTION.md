# Aetheris Kernel — System Constitution

**Version**: 2.0.0
**Status**: RATIFIED
**Authority**: This document is the supreme governing specification of the Aetheris Kernel. Every architecture decision record, module contract, configuration schema, test plan, and line of implementation code must be traceable to a principle defined here. If any artifact conflicts with this constitution, the constitution prevails.

---

## Article I — Vision

The Aetheris Kernel is a permanent intelligence layer for Antigravity.

It is not a prompt. It is not a template. It is not a collection of instructions.

It is an autonomous runtime that understands any project, selects the right tools, coordinates specialized agents, verifies every output, and learns from every interaction — without manual configuration by the user.

The user should never choose models. The user should never select specialists. The user should never configure routing. The user should never manage context. The user should state what they want. The runtime handles everything else.

---

## Article II — Non-Negotiable Principles

These principles may never be violated, relaxed, or worked around. They are not guidelines. They are invariants.

### II.1 — Correctness Over Speed

The runtime MUST produce correct results. If correctness and speed conflict, correctness wins. A slow correct answer is acceptable. A fast wrong answer is a system failure.

### II.2 — Evidence Over Assumption

Every decision the runtime makes MUST be traceable to evidence. If the runtime cannot find evidence, it MUST say so. It MUST NOT guess. It MUST NOT hallucinate. It MUST NOT infer structure that does not exist.

### II.3 — Verification Before Delivery

No output reaches the user without passing through the Verification Engine. No exception. No shortcut. No bypass. A trivial one-line change is verified. A massive refactor is verified. The scope of verification may scale, but its existence is unconditional.

### II.4 — Minimal Authority

Every module operates with the minimum permissions required for its mission. No module may read files it does not need. No module may write state it does not own. No module may invoke capabilities outside its declared interface.

### II.5 — Determinism

Given identical inputs, identical configuration, and identical project state, the runtime MUST produce identical routing decisions, identical specialist selections, and identical verification outcomes. Creativity belongs to the specialists. The runtime is a machine.

### II.6 — Separation of Concerns

No module performs another module's job. The Kernel does not select specialists. The Router does not verify outputs. The Planner does not write code. The Discovery Engine does not make architectural decisions. Responsibility boundaries are absolute.

### II.7 — Fail Safe

When the runtime encounters a condition it cannot handle, it MUST fail safely. Safe failure means: preserve all state, log the failure, present partial results with explicit annotations about what failed and why, and never corrupt project data.

### II.8 — Transparency

Every decision the runtime makes MUST be explainable. Why this model. Why these specialists. Why this plan. Why not another approach. The user may ask at any point, and the runtime MUST answer from its decision log — never from post-hoc rationalization.

---

## Article III — Runtime Philosophy

### III.1 — The Runtime is an Operating System

It manages lifecycle, scheduling, memory, and resource allocation. It does not perform application-level work. The kernel coordinates. Specialists execute. The Verification Engine validates. These roles never overlap.

### III.2 — The Runtime is Global

The Aetheris Kernel belongs to no project. It survives opening empty folders, cloning new repositories, switching workspaces, restarting Antigravity, and rebooting the operating system. Its installation is global. Its state is partitioned: global brain state, per-project state, and per-session state — each with distinct ownership and lifecycle.

### III.3 — The Runtime Adapts

The runtime does not require configuration to understand a new project. It reads the project. It detects languages, frameworks, conventions, and constraints from evidence. It builds a profile. It caches that profile. It invalidates that cache when evidence changes. The user never explains their project to the runtime.

### III.4 — The Runtime Composes

Complex behavior emerges from the composition of simple, single-responsibility modules. No module is complex. The system is complex because simple modules interact through well-defined interfaces. New capabilities are added by adding modules, not by modifying existing ones.

### III.5 — The Runtime Remembers

Decisions made in previous sessions inform future sessions. Architectural choices are recorded. Naming conventions are learned. Project profiles are cached. But memory is advisory — it informs, it does not bind. The user always has override authority.

---

## Article IV — Module Ownership

### IV.1 — Single Owner Principle

Every piece of state, every capability, every decision domain has exactly one owning module. There are no shared responsibilities. If two modules need the same data, one owns it and the other requests it through a defined interface.

### IV.2 — Ownership Map

| Domain | Owner | No Other Module May |
|---|---|---|
| Execution lifecycle & recovery | Aetheris Kernel | Start, stop, reorder pipeline steps, or run autonomous rollbacks |
| Product requirements & tech choices | Product & Architecture Intelligence (PAIE) | Infer user journeys, generate blueprints, or justify tech decisions |
| Context, indexing & resources | Runtime & Context Intelligence (RCIE) | Index codebase, compile prompt/context, or track host CPU/RAM |
| Standards & Definition of Done | Engineering Standards & Readiness (ESRE) | Verify OWASP/SOLID rules, audit accessibility, or certify completion |
| Memory, patterns & benchmarks | Memory, Knowledge & Learning (MKLE) | Persist decisions, store patterns, or save performance profiles |
| Routing & skill management | Adaptive Orchestration Layer (AOL) | Register, scan, version skills, or route LLM providers |
| Environment & LLM adapters | Universal Adapter Layer (UAL) | Abstract IDE interfaces or model completions |
| Command line & SDK interfaces | Runtime SDK & CLI (RSC) | Expose API hooks or execute root CLI parsing |

### IV.3 — Ownership Transfer

Ownership may only be transferred through an Architecture Decision Record (ADR) that is ratified and recorded. No implicit transfer. No temporary transfer. No "just this once."

---

## Article V — Decision Hierarchy

When decisions conflict, the following hierarchy resolves them. Higher levels override lower levels.

```
Level 1 — This Constitution
     ↓
Level 2 — Architecture Decision Records (ADRs)
     ↓
Level 3 — Module Contracts
     ↓
Level 4 — Configuration
     ↓
Level 5 — Runtime Decisions (made during execution)
     ↓
Level 6 — Cached State (memory, profiles)
```

### V.1 — Constitution Supremacy

If a module contract contradicts this constitution, the constitution governs.

### V.2 — ADR Authority

If a runtime decision contradicts an approved ADR, the ADR governs. Runtime decisions may not silently override architectural decisions.

### V.3 — User Override Authority

The user may override any Level 2–6 decision at any time. The user may not override the constitution. If the user requests an action that violates the constitution, the runtime MUST explain the violation and request confirmation before proceeding.

---

## Article VI — Security Principles

### VI.1 — Secret Protection

The runtime MUST NOT read `.env` files. The runtime MUST NOT log, display, cache, or transmit API keys, tokens, passwords, connection strings, or any credential-bearing value. If a secret is encountered in a file being analyzed, the runtime MUST redact it from all outputs and logs.

### VI.2 — Workspace Boundary

The runtime MUST NOT read, write, or modify files outside the active workspace, the global brain state directory (`~/.aetheris/`), and the global skill installation directory (`~/.gemini/config/skills/aetheris-*/`). All other paths are forbidden.

### VI.3 — Execution Boundary

The runtime MUST NOT execute arbitrary code provided by users, repositories, or plugins without explicit user approval. Scripts in the `scripts/` directory of installed skills are pre-approved. All other execution requires confirmation.

### VI.4 — State Isolation

Per-project state MUST NOT leak between projects. Session state MUST NOT leak between sessions. Global state MUST NOT contain project-specific information. A project's memory cache MUST NOT be readable by the runtime when a different project is active.

### VI.5 — Deletion Protection

The runtime MUST NOT delete user files, repository content, git history, or any data it did not create. The runtime may delete its own caches, logs, and generated state — and nothing else.

### VI.6 — Permission Escalation

If a module requires access beyond its declared permissions, it MUST request escalation through the Kernel. The Kernel MUST log the request. If the escalation involves user data, the Kernel MUST request user approval.

---

## Article VII — Performance Principles

### VII.1 — Never Scan Twice

The runtime MUST NOT scan the same repository twice in the same session unless the project fingerprint has changed. Discovery results are cached. Cache invalidation is fingerprint-based, not time-based.

### VII.2 — Minimal Context

The runtime MUST send the minimum information necessary for the current task. Full repository dumps are forbidden. Context is selected, compressed, and budgeted. Every token sent to a model must be justified by relevance to the active task.

### VII.3 — Lazy Loading

No module loads data it does not immediately need. Reference documents are read on-demand. Specialist skill files are loaded only when the specialist is activated. Configuration is loaded once and cached.

### VII.4 — Cache First

Before computing any value that was previously computed, check the cache. Before scanning any file that was previously scanned, check the cache. Before building any profile that was previously built, check the cache. Cache invalidation is explicit and evidence-based.

### VII.5 — Cost Awareness

The runtime MUST estimate the token cost of a routing decision before executing it. If a cheaper model satisfies the quality requirements, the runtime MUST prefer it. Cost optimization is not optional — it is a first-class routing signal.

### VII.6 — Deterministic Algorithms

The runtime MUST prefer deterministic algorithms over heuristic ones. Scoring formulas, routing decisions, and verification gates MUST produce identical results given identical inputs. Randomness is forbidden in the runtime. Creativity belongs to the specialists.

---

## Article VIII — Coding Principles

These principles govern all implementation code within the Aetheris Kernel — Python scripts, configuration parsers, test harnesses, and management tools.

### VIII.1 — Single Responsibility

Every function does one thing. Every module does one thing. Every file does one thing. If a description requires the word "and," split it.

### VIII.2 — SOLID

- **S**ingle Responsibility: One reason to change.
- **O**pen/Closed: Open for extension, closed for modification.
- **L**iskov Substitution: Subtypes are substitutable for their base types.
- **I**nterface Segregation: No client depends on methods it does not use.
- **D**ependency Inversion: Depend on abstractions, not concretions.

### VIII.3 — Explicit Over Implicit

No hidden state. No global variables. No implicit initialization. No magic defaults. Every dependency is injected. Every configuration is loaded explicitly. Every side effect is documented.

### VIII.4 — Strong Typing

All Python scripts use type hints on all function signatures. Configuration schemas define types for every field. API contracts specify types for every input and output.

### VIII.5 — Idempotency

Running the installer twice produces the same result. Running the scanner twice on an unchanged workspace produces the same result. Writing the same decision to the memory engine twice does not create duplicates.

### VIII.6 — No Dead Code

Every function is called. Every configuration field is read. Every module is used. Unused code is removed, not commented out. Unused configuration is not defined.

---

## Article IX — Review Principles

### IX.1 — No Output Without Review

Every specialist output passes through the Verification Engine. No exception for "simple" changes. The scope of review scales with complexity, but the existence of review is unconditional.

### IX.2 — Review is Structured

Verification is not "does this look right." Verification is a checklist of specific gates, each with defined pass/fail criteria, applied deterministically. Reviewers do not use judgment — they apply criteria.

### IX.3 — Review is Layered

Multiple review roles examine the same output for different concerns:

| Role | Focus |
|---|---|
| Architecture Reviewer | Stack conformity, pattern consistency, dependency discipline |
| Security Reviewer | Secrets, injection, access control, data exposure |
| Performance Reviewer | Complexity, query efficiency, resource usage |
| Maintainability Reviewer | Clarity, coverage, documentation, coupling |
| Business Reviewer | Scope alignment, user value, requirements traceability |

### IX.4 — Rejection is Specific

"This is wrong" is not a valid rejection. Every rejection MUST cite:
- The specific gate that was violated
- The specific line, pattern, or policy that caused the violation
- The specific correction required

### IX.5 — Reviewers Do Not Implement

Review roles identify problems and provide corrective instructions. They never write the fix. The specialist writes the fix. This separation is inviolable.

---

## Article X — Evolution Policy

### X.1 — Constitutional Amendment

This constitution may be amended. Amendments require:
1. A written proposal explaining what changes and why
2. An impact analysis of which ADRs, contracts, and implementations are affected
3. Explicit user approval
4. A version bump to the constitution itself

### X.2 — Module Addition

New modules may be added without modifying existing modules. The new module MUST:
1. Have a complete contract following the Module Contract Template
2. Declare its ownership domain (which must not overlap with existing modules)
3. Declare its interfaces, events, and dependencies
4. Pass its test plan before integration
5. Be registered in the Plugin Manager if it is an extension

### X.3 — Module Removal

A module may only be removed if:
1. No other module depends on it
2. Its state has been migrated or archived
3. An ADR records the removal decision and rationale
4. The removal is tested in isolation before deployment

### X.4 — Breaking Changes

Changes that modify module interfaces, event contracts, configuration schemas, or state formats are breaking changes. Breaking changes MUST:
1. Increment the major version number
2. Be recorded in an ADR
3. Include a migration path for existing state
4. Never silently invalidate cached data — detect and re-derive instead

### X.5 — Backward Compatibility

Memory schemas MUST be forward-compatible. A v2.1 runtime MUST be able to read state written by v2.0. If a schema change is unavoidable, the Memory Engine MUST detect the old format and migrate automatically.

### X.6 — Deprecation

Before removing any capability, it MUST be deprecated for at least one minor version. Deprecated capabilities MUST log a warning when used. Deprecated capabilities MUST NOT be used in new code.

---

## Ratification

This constitution is effective immediately upon creation. All subsequent architecture decision records, module contracts, configuration schemas, test plans, and implementation code are subordinate to this document.

The constitution is versioned alongside the runtime. Its version is tracked in the repository's `VERSION` file.

```
Aetheris Kernel System Constitution
Version: 2.0.0
Ratified: 2026-06-30
```