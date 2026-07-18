"""
DynamicSkillEvolutionEngine (DSEE) — SPEC-062.

Analyses skill performance metrics over time and triggers evolution:
  - Skills with declining SRE scores get re-benchmarked
  - Underperforming skills are flagged for replacement
  - New skill variants are proposed based on successful patterns
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class DynamicSkillEvolutionEngine:
    """SPEC-062 Dynamic Skill Evolution Engine."""

    DECLINE_THRESHOLD  = 0.10   # >10% score drop triggers evolution
    MIN_SAMPLE_SIZE    = 5      # need at least 5 runs before evolving
    REPLACEMENT_SCORE  = 0.60   # skills below this are replaced

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self._workspace = Path(workspace_path).resolve()
        self._store     = event_store
        self._session   = session_id
        self._perf_dir  = self._workspace / ".aetheris" / "benchmarks" / "skills"
        self._perf_dir.mkdir(parents=True, exist_ok=True)

    def record_skill_performance(self, skill_name: str, sre_score: float,
                                  task_type: str = ""):
        """Record one skill execution result."""
        perf_file = self._perf_dir / f"{skill_name}.json"
        data = self._load_perf(perf_file)
        data.setdefault("runs", []).append({
            "score": sre_score, "task_type": task_type, "ts": time.time()
        })
        data["runs"] = data["runs"][-100:]   # keep last 100
        data["avg_score"]    = round(sum(r["score"] for r in data["runs"]) /
                                     len(data["runs"]), 4)
        data["last_updated"] = time.time()
        perf_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def analyse_skills(self) -> List[Dict[str, Any]]:
        """Return list of skills needing evolution action."""
        actions = []
        for f in self._perf_dir.glob("*.json"):
            data = self._load_perf(f)
            runs = data.get("runs", [])
            if len(runs) < self.MIN_SAMPLE_SIZE:
                continue

            avg   = data.get("avg_score", 1.0)
            early = sum(r["score"] for r in runs[:5]) / 5
            late  = sum(r["score"] for r in runs[-5:]) / 5
            delta = late - early

            if avg < self.REPLACEMENT_SCORE:
                actions.append({
                    "skill":  f.stem,
                    "action": "REPLACE",
                    "reason": f"Average score {avg:.2f} below threshold {self.REPLACEMENT_SCORE}",
                    "avg_score": avg,
                })
            elif delta < -self.DECLINE_THRESHOLD:
                actions.append({
                    "skill":  f.stem,
                    "action": "REBENCHMARK",
                    "reason": f"Score declined {abs(delta):.2f} over last 5 runs",
                    "delta":  round(delta, 4),
                    "avg_score": avg,
                })

        return actions

    def _load_perf(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def evolve_skill(self, skill_name: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger skill evolution (mock/shim)."""
        return {"status": "EVOLVED", "skill": skill_name, "timestamp": time.time()}
