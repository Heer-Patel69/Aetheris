# Module: Resource Router

## Header
- Name: Resource Router
- Version: 2.1.0
- Purpose: Select the smallest effective team of specialists and recommend the optimal model for the current task.
- Owner: Resource Router
- Dependencies: Config Manager, Project Discovery, Event Bus, Telemetry Engine
- Security Level: HIGH
- Performance Target: Routing selection and cost estimation completed in <150ms.

## Mission
The Resource Router exists solely to select the minimum effective specialist team and recommend the optimal model. It is forbidden from programmatically switching models, executing tasks, or verifying outputs.

## Responsibilities
- Score candidate specialists from the 217-agent roster against the task context and project profile.
- Apply the confidence threshold ($S \ge 85$) to filter active specialists.
- Classify task complexity (Trivial, Moderate, Complex, Architectural) to determine the team size bracket.
- Recommend the optimal active model from `models.yaml` based on task context depth and reasoning weight.
- Estimate the token size and resource costs of the execution plan using the pricing tables in `costs.yaml`.

## Explicitly Forbidden
The Resource Router MUST NOT:
- Switch models programmatically (platform limitation — the host IDE controls active models).
- Execute specialist actions or write codebase modifications.
- Run quality gate checks on specialist outputs (verification engine handles that).
- Expose credentials or keys during provider mappings.
- Enforce rigid specialist team caps (caps must scale dynamically with complexity).

## Inputs
- Execution Plan (from Planner)
- Context Package (from Context Engine)
- Project Profile (from Memory Engine)
- Configuration: `specialists.yaml` (roster index), `models.yaml` (model properties), `costs.yaml` (pricing index)

## Outputs
- Structured Roster Recommendation (JSON containing recommended model, active specialists list with confidence scores, estimated token counts, and advisory cost estimation)

## State
- Persistent State: None
- Temporary State: Current session routing scores
- Cache: None
- Configuration: Specialist activation thresholds ($S \ge 85$), complexity brackets
- Runtime Variables: Active workspace root, active model name

## Public API
- `Router.RouteTask(plan, context, profile) -> RoutingRecommendation`
- `Router.ScoreSpecialist(agent_name, task, profile) -> ConfidenceScore`
- `Router.EstimateRunCost(plan, context, model_name) -> CostEstimation`

## Internal API
- `_calculateS(intent_match, stack_relevance, risk_weight, context_fit, cost_efficiency) -> Float`
- `_determineComplexityBracket(plan) -> ComplexityString`
- `_checkRosterConstraints(roster) -> bool`

## Event Subscriptions
- On PlanCreated

## Events Published
- RosterRecommended(recommendation)
- ModelMismatchWarning(active, recommended)
- RoutingFailed(reason)

## Failure Conditions
- If no specialist scores above threshold ($S < 85$):
  Assign Kernel generalist mode -> log warning to telemetry -> publish RosterRecommended -> continue
- If active model context limit is smaller than Context Package size:
  Publish ModelMismatchWarning -> request user selection or trigger Context Engine to prune -> log telemetry -> continue
- If configuration file missing or corrupt:
  Log error -> fallback to default model settings -> assign default specialists -> continue

## Quality Standards
- Maximum latency: 150 ms
- Activation threshold: $S \ge 85$ (no specialist below this may activate unless explicitly requested)
- Cost estimation accuracy: Within ±15% of real billing

## Security Rules
- Roster recommendations must never expose internal user profiles.
- Scoring formulas must be deterministic and run in memory (no external command dependencies).
- Strictly validate agent names to prevent command injections.

## Recovery Strategy
Fallback to default generalist -> Select cheapest model -> Request user selection -> Abort

## Testing Strategy
- Unit Tests: Verify confidence score formula calculation, complexity classification brackets.
- Integration Tests: Test specialist routing for a mock database modification task.
- Performance Tests: Verify execution overhead remains below 150ms.

## Success Criteria
- Specialists are selected based on stack indicators (e.g., Supabase task routes to database-optimizer).
- Recommends the cheaper model when complexity is low (Trivial tasks).
- Output is deterministic: identical inputs yield identical team scores.
- Cost estimate is always calculated and included.
