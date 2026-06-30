# Module: Planner

## Header
- Name: Planner
- Version: 2.1.0
- Purpose: Decompose user tasks into ordered, dependency-aware execution plans.
- Owner: Planner
- Dependencies: Config Manager, Project Discovery, Context Engine, Event Bus
- Security Level: MEDIUM
- Performance Target: Plan generation completed in <300ms.

## Mission
The Planner exists solely to decompose tasks into ordered execution plans before routing begins. It is forbidden from writing code, executing tasks, or selecting specialists.

## Responsibilities
- Decompose complex user intents into atomic, sequential task steps.
- Map dependencies between tasks to establish a correct execution order.
- Identify technical and structural risks associated with each task step.
- Define explicit, measurable success criteria for each task.
- Generate structured execution plans matching the planner schema.

## Explicitly Forbidden
The Planner MUST NOT:
- Write source code or modifications.
- Execute terminal commands or file changes.
- Select specialists or model paths (that is the Resource Router's job).
- Skip dependency validation.
- Assume architecture patterns (it must query the profile).

## Inputs
- User request context
- Project Profile (from Memory Engine)
- Context Package (from Context Engine)
- Active session history

## Outputs
- Structured Execution Plan (JSON/YAML containing goal, tasks list, dependencies, risks, execution order, and success criteria)

## State
- Persistent State: None
- Temporary State: Current session plan tree
- Cache: None
- Configuration: Maximum task steps limit, default success templates
- Runtime Variables: Session ID

## Public API
- `Planner.CreatePlan(request, profile, context) -> ExecutionPlan`
- `Planner.ValidatePlan(plan) -> ValidationResult`
- `Planner.DecomposeTask(task_desc) -> ListOfSubtasks`

## Internal API
- `_checkCircularDependencies(tasks) -> bool`
- `_assessRiskLevel(task_desc, profile) -> RiskRating`
- `_inferSuccessCriteria(task, profile) -> String`

## Event Subscriptions
- On ContextReady
- On TaskCreated

## Events Published
- PlanCreated(plan)
- PlanValidationFailed(errors)
- PlanExecutionAborted(reason)

## Failure Conditions
- If circular dependency detected in plan:
  Halt plan generation -> publish PlanValidationFailed -> re-order tasks sequentially -> log to telemetry -> continue
- If task complexity exceeds limits (e.g., >10 steps):
  Split plan into phased sub-goals -> request user approval for Phase 1 -> log to telemetry -> continue
- If success criteria cannot be inferred:
  Fallback to default validation template -> prompt user to confirm success criteria -> continue

## Quality Standards
- Maximum execution latency: 300 ms
- Output determinism: Identical inputs must yield structurally congruent plans
- Every task step must have at least one defined success criterion

## Security Rules
- Plan steps must never specify execution of unsafe scripts or commands.
- Verify that plan dependencies do not involve paths outside the workspace perimeter.
- Plan descriptions must not contain sensitive codebase secrets.

## Recovery Strategy
Fallback to linear sequential plan -> Decompose into smaller phases -> Prompt user for confirmation -> Abort

## Testing Strategy
- Unit Tests: Verify circular dependency checking, task decomposition logic.
- Integration Tests: Test plan creation for a mock database migration task.
- Performance Tests: Verify execution overhead remains below 300ms.

## Success Criteria
- Execution plan lists all steps required to achieve the goal.
- Steps are ordered correctly (e.g., database changes occur before API changes).
- No circular dependencies exist in the output plan.