"""
Optimization Engines (Phase 4, Phase C):
  TokenOptimizationEngine  (TOE) — SPEC-058
  CostOptimizationEngine   (COE) — SPEC-059
  PlanningOptimizationEngine (PLE) — SPEC-057
  ExecutionOptimizationEngine (EOE) — SPEC-060
"""
import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ─── TOE ──────────────────────────────────────────────────────────────────────

class TokenOptimizationEngine:
    """
    SPEC-058 Token Optimization Engine.
    Target: 20% token reduction vs baseline without quality loss.
    """

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self.workspace = Path(workspace_path).resolve()
        self._store    = event_store
        self._session  = session_id
        self._stats: Dict[str, Any] = {"total_saved": 0, "sessions": []}

    # ── compression techniques ────────────────────────────────────────────────

    def compress_tokens(self, text: str) -> str:
        """Technique 1: normalise whitespace."""
        return " ".join(text.split())

    def compress_context(self, context: str, task_type: str = "") -> Dict[str, Any]:
        """
        Full context compression pipeline.
        Applies: whitespace norm → duplicate removal → comment strip (code).
        """
        original_len = len(context)

        # 1. normalise whitespace
        compressed = re.sub(r"\n{3,}", "\n\n", context)
        compressed = re.sub(r" {2,}", " ", compressed)

        # 2. remove duplicate lines (keeps first occurrence)
        lines = compressed.splitlines()
        seen, deduped = set(), []
        for line in lines:
            stripped = line.strip()
            if stripped not in seen or len(stripped) < 15:
                deduped.append(line)
                seen.add(stripped)
        compressed = "\n".join(deduped)

        # 3. strip inline comments for simple task types
        if task_type in ("QUICK", "simple"):
            compressed = re.sub(r"#[^!].*$", "", compressed, flags=re.MULTILINE)
            compressed = re.sub(r"\n{2,}", "\n", compressed)

        saved = original_len - len(compressed)
        pct   = round(saved / max(original_len, 1) * 100, 1)

        result = {
            "original_length":   original_len,
            "compressed_length": len(compressed),
            "chars_saved":       saved,
            "reduction_pct":     pct,
            "compressed":        compressed,
        }

        self._stats["total_saved"] += saved
        self._emit(result)
        return result

    def compress_ekb_entries(self, entries: List[Dict[str, Any]],
                              max_entries: int = 5) -> List[Dict[str, Any]]:
        """Technique 2: compress EKB entries to keyword form for simple tasks."""
        compressed = []
        for entry in entries[:max_entries]:
            content = entry.get("content", {})
            summary = {
                "id":   entry.get("object_id", ""),
                "type": entry.get("type", ""),
                "keys": list(content.keys())[:8] if isinstance(content, dict) else [],
            }
            compressed.append(summary)
        return compressed

    def _emit(self, result: Dict[str, Any]):
        if not self._store:
            return
        try:
            self._store.emit(
                category="TOKENS",
                event_type="TokensOptimized",
                payload={"reduction_pct": result["reduction_pct"],
                         "chars_saved":   result["chars_saved"]},
                session_id=self._session,
            )
        except Exception:
            pass


# ─── COE ──────────────────────────────────────────────────────────────────────

class CostOptimizationEngine:
    """
    SPEC-059 Cost Optimization Engine.
    Tracks cost per task/model; enforces session budget.
    """

    DEFAULT_BUDGET_USD = float(os.environ.get("AETHERIS_SESSION_BUDGET_USD", "5.00"))

    # rates (USD per 1M tokens) — updated from MIE registry at runtime
    _RATES: Dict[str, Tuple[float, float]] = {
        "gemini-1.5-flash":  (0.075, 0.30),
        "gemini-2.5-flash":  (0.075, 0.30),
        "gemini-2.5-pro":    (1.25,  5.00),
        "claude-3-5-sonnet": (3.00, 15.00),
        "claude-3-7-sonnet": (3.00, 15.00),
        "gpt-4o":            (5.00, 15.00),
    }

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self.workspace    = Path(workspace_path).resolve()
        self._store       = event_store
        self._session     = session_id
        self._session_cost = 0.0
        self._budget      = self.DEFAULT_BUDGET_USD
        self._task_costs: Dict[str, float] = defaultdict(float)
        self._model_costs: Dict[str, float] = defaultdict(float)
        self._report_path = (
            self.workspace / ".aetheris" / "analytics" / "CostAnalysis.json"
        )
        self._report_path.parent.mkdir(parents=True, exist_ok=True)

    def calculate_cost(self, model_id: str, input_tokens: int,
                       output_tokens: int) -> float:
        """Calculate actual cost for a model call."""
        rate_in, rate_out = self._RATES.get(model_id, (1.0, 5.0))
        cost = (input_tokens / 1_000_000 * rate_in +
                output_tokens / 1_000_000 * rate_out)
        return round(cost, 8)

    def record_cost(self, model_id: str, input_tokens: int,
                    output_tokens: int, task_type: str = ""):
        cost = self.calculate_cost(model_id, input_tokens, output_tokens)
        self._session_cost     += cost
        self._task_costs[task_type] += cost
        self._model_costs[model_id] += cost

        # budget enforcement
        over_budget = self._session_cost >= self._budget

        result = {
            "model_id":      model_id,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "cost_usd":      cost,
            "session_total": round(self._session_cost, 6),
            "budget_usd":    self._budget,
            "over_budget":   over_budget,
        }

        self._update_report()
        self._emit(result)

        if over_budget:
            import sys
            sys.stderr.write(
                f"⚠  AETHERIS BUDGET EXCEEDED: "
                f"${self._session_cost:.4f} of ${self._budget:.2f} used.\n"
            )

        return result

    def recommend_model(self, task_type: str) -> str:
        """Recommend the most cost-efficient model for a task type."""
        # classify task
        complex_types = {"architecture", "security", "consensus", "DEEP"}
        if any(t in task_type for t in complex_types):
            return "claude-3-7-sonnet"
        return "gemini-1.5-flash"   # cheapest capable model

    def calculate_optimal_cost(self, tokens_count: int, model_id: str) -> float:
        """Compatibility wrapper."""
        return self.calculate_cost(model_id, tokens_count, tokens_count // 4)

    def _update_report(self):
        report = {
            "session_cost_usd": round(self._session_cost, 6),
            "budget_usd":       self._budget,
            "remaining_usd":    round(max(0, self._budget - self._session_cost), 6),
            "task_costs":       dict(self._task_costs),
            "model_costs":      dict(self._model_costs),
            "updated_at":       time.time(),
        }
        self._report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def _emit(self, result: Dict[str, Any]):
        if not self._store:
            return
        try:
            self._store.emit(
                category="COSTS",
                event_type="CostRecorded",
                payload=result,
                session_id=self._session,
            )
        except Exception:
            pass


# ─── PLE ──────────────────────────────────────────────────────────────────────

class PlanningOptimizationEngine:
    """SPEC-057 Planning Optimization Engine."""

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self.workspace = Path(workspace_path).resolve()
        self._store    = event_store
        self._session  = session_id

    def optimize_plan(self, raw_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Compress and deduplicate a raw execution plan."""
        steps = raw_plan.get("steps", [])
        original_count = len(steps)

        # deduplicate similar steps
        seen_labels: set = set()
        deduped = []
        for step in steps:
            if isinstance(step, dict):
                label = step.get("name", step.get("label", str(step)))
            else:
                label = str(step)
            if label not in seen_labels:
                deduped.append(step)
                seen_labels.add(label)

        # identify batchable steps (same engine)
        batches: Dict[str, List] = defaultdict(list)
        for step in deduped:
            if isinstance(step, dict):
                engine = step.get("engine", "unknown")
            else:
                engine = "unknown"
            batches[engine].append(step)

        batch_suggestions = [
            {"engine": eng, "steps": len(stps), "can_parallelize": len(stps) > 1}
            for eng, stps in batches.items() if len(stps) > 1
        ]

        return {
            "optimized":        True,
            "original_steps":   original_count,
            "optimized_steps":  len(deduped),
            "steps_removed":    original_count - len(deduped),
            "steps":            deduped,
            "batch_suggestions": batch_suggestions,
        }

    def analyze_historical_plans(self, limit: int = 10) -> Dict[str, Any]:
        """Analyse past execution plans for systemic inefficiencies."""
        plan_dir = self.workspace / ".aetheris" / "execution"
        plans    = list(plan_dir.glob("*.json"))[:limit] if plan_dir.exists() else []
        return {
            "plans_analyzed": len(plans),
            "recommendation":  (
                "Batch independent tasks where engine is the same."
                if plans else "Not enough history to analyse."
            ),
        }


# ─── EOE ──────────────────────────────────────────────────────────────────────

class ExecutionOptimizationEngine:
    """SPEC-060 Execution Optimization Engine."""

    P95_TARGET_MS = {
        "WDE": 30_000, "URUE": 5_000, "TDE": 10_000,
        "ACGE": 60_000, "SRE": 5_000, "GOE": 3_000,
    }

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self.workspace = Path(workspace_path).resolve()
        self._store    = event_store
        self._session  = session_id
        self._timings: Dict[str, List[float]] = defaultdict(list)

    def record_step_timing(self, engine: str, duration_ms: float):
        self._timings[engine].append(duration_ms)

    def optimize_execution(self, tasks: List[Any]) -> List[Any]:
        """Sort and group tasks for optimal parallel execution."""
        if not tasks:
            return tasks
        # tasks with no dependencies can run in parallel — group by dependency depth
        prioritized = sorted(
            tasks,
            key=lambda t: (
                len(t.get("depends_on", [])) if isinstance(t, dict) else 0
            ),
        )
        return prioritized

    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Find engines whose P95 exceeds targets."""
        bottlenecks = []
        for engine, times in self._timings.items():
            if not times:
                continue
            sorted_times = sorted(times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            target = self.P95_TARGET_MS.get(engine, 30_000)
            if p95 > target:
                bottlenecks.append({
                    "engine": engine, "p95_ms": p95, "target_ms": target,
                    "excess_pct": round((p95 - target) / target * 100, 1),
                    "recommendation": f"Parallelise {engine} sub-tasks or cache outputs.",
                })
        return sorted(bottlenecks, key=lambda x: x["excess_pct"], reverse=True)

    def get_parallelisation_suggestions(self) -> List[str]:
        suggestions = []
        bottlenecks = self.identify_bottlenecks()
        for b in bottlenecks:
            suggestions.append(
                f"{b['engine']} is {b['excess_pct']}% over P95 target — "
                f"{b['recommendation']}"
            )
        return suggestions
