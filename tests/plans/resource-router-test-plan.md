# Test Plan: Resource Router

## 1. Scope
This test plan covers specialist routing confidence checks, complexity bracket assignments, model selection recommendation, and token/cost estimations.

## 2. Test Cases

### 2.1 — Specialist Routing Scores (Pass)
- **Condition**: Route a frontend component task on a React + TypeScript project.
- **Expected Outcome**: Matches the `frontend-developer` and `ui-designer` specialists with confidence scores $S \ge 85$, while ignoring python or backend specialists.

### 2.2 — Model Recommendation Logic (Pass)
- **Condition**: Evaluate model recommendations for a Trivial task versus an Architectural task.
- **Expected Outcome**: Recommends the cheaper, faster model (e.g. `gemini-3.5-flash`) for the Trivial task, and the deep reasoning model (e.g. `claude-opus-4.6`) for the Architectural task.

### 2.3 — Cost Estimation Heuristics (Pass)
- **Condition**: Calculate costs for a plan requiring 15,000 input tokens and 2,000 output tokens on a specific model.
- **Expected Outcome**: Cost estimation matches pricing rates in `costs.yaml` within a $\pm15\%$ margin.

### 2.4 — Missing Specialist Config (Fail / Recovery)
- **Condition**: Load router when `specialists.yaml` is corrupted.
- **Expected Outcome**: Router falls back to default generalist routing, logs warning, and pipeline continues.

## 3. Performance Benchmarks
- Routing selection and cost estimation MUST complete in **<150ms**.
- Scoring confidence calculation for 20 specialists must complete in **<20ms**.

## 4. Security Validation Scenarios
- Verify that no credentials or keys are exposed during model provider config mappings.
- Validate that specialist name strings match sanitization rules to block command injections.