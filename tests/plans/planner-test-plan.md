# Test Plan: Planner

## 1. Scope
This test plan covers the task decomposition, dependency ordering, circular dependency checks, and success criteria mappings.

## 2. Test Cases

### 2.1 — Successful Plan Generation (Pass)
- **Condition**: Generate an execution plan for a database modification task.
- **Expected Outcome**: Tasks are decomposed sequentially, dependencies are mapped (e.g. schema migration before frontend display), and clear success criteria are defined for each step.

### 2.2 — Circular Dependency Detection (Fail / Recovery)
- **Condition**: Inject a circular dependency loop (e.g. Task A depends on Task B, Task B depends on Task A).
- **Expected Outcome**: Planner detects the loop, rejects the plan, reorganizes tasks in a linear sequential chain, logs a warning, and continues.

### 2.3 — Task Step Limits (Edge Case)
- **Condition**: Decompose a highly complex intent that results in more than 10 steps.
- **Expected Outcome**: Planner groups tasks into phased sub-goals (e.g. Phase 1: Database, Phase 2: API) and requests user approval for Phase 1.

### 2.4 — Success Criteria Validation (Pass)
- **Condition**: Verify that generated plans map template validations.
- **Expected Outcome**: Every step contains a valid success metric string (no placeholders allowed).

## 3. Performance Benchmarks
- Plan generation and validation MUST complete in **<300ms**.
- Dependency checks must execute in **<10ms**.

## 4. Security Validation Scenarios
- Verify that no task steps instruct execution of unsafe bash command lines.
- Verify that path contexts inside the plan are strictly within the workspace boundaries.
