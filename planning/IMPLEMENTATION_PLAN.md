# Implementation Plan — AntiGravity Token Intelligence & Benchmark System (ATIB)

We will build the **AntiGravity Token Intelligence & Benchmark System (ATIB)** as a set of core engines under the `src/intelligence/` namespace to measure, benchmark, analyze, optimize, and log token usage, cost, and coverage metrics across Aetheris execution sessions.

## Proposed Changes

### Component: ATIB Intelligence Subsystems

#### [NEW] [token_intelligence.py](file:///c:/AI/Agency%20owner/aetheris/src/intelligence/token_intelligence.py)
Implements token measurements, tracking cache hit rates, reasoning tokens, costs, errors, retry counts, latency, and context window limits.

#### [NEW] [benchmark_engine.py](file:///c:/AI/Agency%20owner/aetheris/src/intelligence/benchmark_engine.py)
Performs benchmarks on loaded files, context reduction delta, skills/RFCs/SPECs activated versus ignored, and computes overall quality indexes.

#### [NEW] [context_optimizer.py](file:///c:/AI/Agency%20owner/aetheris/src/intelligence/context_optimizer.py)
Scans skills, RFCs, SPECs, resolves dependencies, filters duplicates, and compiles the compressed context representation.

#### [NEW] [cost_analyzer.py](file:///c:/AI/Agency%20owner/aetheris/src/intelligence/cost_analyzer.py)
Maps models to their input/output token cost rates and calculates precise expenses.

#### [NEW] [repository_metrics.py](file:///c:/AI/Agency%20owner/aetheris/src/intelligence/repository_metrics.py)
Computes repository sizes, active departments, lines of code, and department/skill/RFC/SPEC coverage rates.

#### [NEW] [historical_analytics.py](file:///c:/AI/Agency%20owner/aetheris/src/intelligence/historical_analytics.py)
Tracks and records session histories, aggregates averages, and exports the data to JSON files.

#### [NEW] [dashboard_metrics.py](file:///c:/AI/Agency%20owner/aetheris/src/intelligence/dashboard_metrics.py)
Generates the live statistics block to expose live token usage, current model status, and readiness scores.

---

### Component: Aetheris Integration & Tests

#### [MODIFY] [core.py](file:///c:/AI/Agency%20owner/aetheris/src/kernel/core.py)
Integrate the ATIB systems into `AetherisKernel.run_autonomous_loop(...)` to track pre-run repository states, execute context compression, track LLM costs on mock stages, and compile the final Execution Report block.

#### [NEW] [test_atib.py](file:///c:/AI/Agency%20owner/aetheris/tests/test_atib.py)
Wrote full unit tests for all new ATIB engines checking edge cases, cost analysis math, and historical log aggregation.

---

## Verification Plan

### Automated Tests
* Run the unit tests via Python's unittest framework:
  `$env:PYTHONPATH="src;../scripts;tests" ; .venv\Scripts\python -m unittest tests/test_atib.py`
* Verify compliance against the global test suite.
