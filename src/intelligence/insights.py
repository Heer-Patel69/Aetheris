"""
EngineeringInsightsEngine — Phase 4.

Generates actionable recommendations from historical runtime data only.
No mock values — all insights derived from EventStore projections.

Example insights:
  - Unused skills (loaded but never invoked)
  - Frequently loaded RFCs
  - Slow integrations (engine P95 > target)
  - Model cost trends
  - Token compression opportunities
  - Architecture drift signals
  - Verification failure patterns
"""
import time
from collections import Counter
from typing import Any, Dict, List

from runtime.event_store import EventStore


class EngineeringInsightsEngine:
    """Generates engineering insights from live EventStore data."""

    def __init__(self, event_store: EventStore, session_id: str = ""):
        self.store    = event_store
        self._session = session_id

    # ── top-level report ──────────────────────────────────────────────────────

    def generate_report(self, workspace_id: str = "") -> Dict[str, Any]:
        """Generate a full insights report for a workspace."""
        events = list(self.store.iter_all())
        if workspace_id:
            events = [e for e in events if e.workspace_id == workspace_id]

        return {
            "generated_at":              time.time(),
            "total_events_analyzed":     len(events),
            "unused_skills":             self.unused_skills(events),
            "frequently_loaded_rfcs":    self.frequent_rfcs(events),
            "slow_integrations":         self.slow_integrations(events),
            "model_cost_trends":         self.model_cost_trends(events),
            "token_compression_opps":    self.token_compression_opportunities(events),
            "verification_failures":     self.verification_failure_patterns(events),
            "architecture_drift":        self.architecture_drift_signals(events),
        }

    # ── individual insights ───────────────────────────────────────────────────

    def unused_skills(self, events: List) -> List[Dict[str, Any]]:
        """Skills that appear in SKILL events with 0 invocations."""
        loaded = Counter()
        invoked = Counter()
        for ev in events:
            if ev.category == "SKILLS":
                name = ev.payload.get("skill_name", "")
                if ev.event_type == "SkillLoaded":
                    loaded[name] += 1
                elif ev.event_type == "SkillInvoked":
                    invoked[name] += 1
        unused = [
            {"skill": s, "load_count": cnt, "invoke_count": invoked.get(s, 0)}
            for s, cnt in loaded.items()
            if invoked.get(s, 0) == 0
        ]
        return sorted(unused, key=lambda x: x["load_count"], reverse=True)[:10]

    def frequent_rfcs(self, events: List) -> List[Dict[str, Any]]:
        """Top 10 most frequently referenced RFCs."""
        counter = Counter(
            ev.payload.get("rfc_id", "")
            for ev in events if ev.category == "RFCS" and ev.payload.get("rfc_id")
        )
        return [{"rfc_id": r, "references": c}
                for r, c in counter.most_common(10)]

    def slow_integrations(self, events: List) -> List[Dict[str, Any]]:
        """Engine steps that consistently exceed P95 target."""
        timings: Dict[str, List[float]] = {}
        for ev in events:
            if ev.category == "EXECUTION" and ev.event_type == "StageCompleted":
                eng = ev.payload.get("stage", "")
                ms  = ev.payload.get("duration_ms", 0)
                timings.setdefault(eng, []).append(ms)

        slow = []
        TARGETS = {"WDE": 30000, "URUE": 5000, "TDE": 10000,
                   "ACGE": 60000, "SRE": 5000}
        for eng, times in timings.items():
            if len(times) < 3:
                continue
            p95 = sorted(times)[int(len(times) * 0.95)]
            target = TARGETS.get(eng, 30000)
            if p95 > target:
                slow.append({
                    "engine": eng, "p95_ms": p95, "target_ms": target,
                    "sample_count": len(times),
                    "recommendation": f"Cache {eng} outputs or parallelise sub-tasks.",
                })
        return sorted(slow, key=lambda x: x["p95_ms"], reverse=True)

    def model_cost_trends(self, events: List) -> List[Dict[str, Any]]:
        """Per-model cumulative cost from event history."""
        model_costs: Dict[str, float] = {}
        for ev in events:
            if ev.category == "COSTS" and ev.event_type == "CostRecorded":
                mid  = ev.payload.get("model_id", "unknown")
                cost = ev.payload.get("cost_usd", 0.0)
                model_costs[mid] = model_costs.get(mid, 0.0) + cost
        return sorted(
            [{"model_id": m, "total_cost_usd": round(c, 6)}
             for m, c in model_costs.items()],
            key=lambda x: x["total_cost_usd"], reverse=True,
        )

    def token_compression_opportunities(
        self, events: List
    ) -> List[Dict[str, Any]]:
        """Sessions where token reduction was below 15% (compression underperforming)."""
        opps = []
        for ev in events:
            if ev.category == "TOKENS" and ev.event_type == "TokensOptimized":
                pct = ev.payload.get("reduction_pct", 100.0)
                if pct < 15.0:
                    opps.append({
                        "session_id":    ev.session_id,
                        "reduction_pct": pct,
                        "recommendation": "Enable Headroom AI compression for this task type.",
                    })
        return opps[:10]

    def verification_failure_patterns(
        self, events: List
    ) -> List[Dict[str, Any]]:
        """Recurring verification failure gates."""
        fails = Counter(
            ev.payload.get("gate", "unknown")
            for ev in events
            if ev.category == "VERIFICATION"
            and not ev.payload.get("passed", True)
        )
        return [{"gate": g, "failure_count": c, "recommendation":
                 f"Review {g} acceptance criteria — failing {c} times."}
                for g, c in fails.most_common(5)]

    def architecture_drift_signals(
        self, events: List
    ) -> List[Dict[str, Any]]:
        """SPECs referenced in decisions but not in any SPEC event (potential drift)."""
        spec_events  = {ev.payload.get("spec_id") for ev in events
                        if ev.category == "SPECS" and ev.payload.get("spec_id")}
        decision_refs = []
        for ev in events:
            if ev.category == "DECISION":
                text = str(ev.payload.get("rationale", ""))
                import re
                refs = re.findall(r"SPEC-\d+", text)
                decision_refs.extend(refs)

        drift = Counter(
            r for r in decision_refs if r not in spec_events
        )
        return [{"spec_id": s, "decision_mentions": c,
                 "recommendation": f"{s} referenced in decisions but no usage event emitted."}
                for s, c in drift.most_common(5)]
