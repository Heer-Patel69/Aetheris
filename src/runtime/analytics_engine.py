"""
AnalyticsEngine — Compute session/workspace/global analytics from the EventStore (Phase 4).

Provides structured analytics for all three Mission Control modes:
  - Global: across all workspaces and sessions
  - Workspace: scoped to the current workspace
  - Session: single execution session
"""
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from runtime.event_store import EventStore


class AnalyticsEngine:
    """
    Computes analytics from EventStore data.  All values are derived from
    real events — no mocked or hardcoded statistics.
    """

    def __init__(self, event_store: EventStore):
        self.store = event_store

    # ── session analytics ─────────────────────────────────────────────────────

    def session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Full analytics for one execution session."""
        events = self.store.read_session(session_id)
        if not events:
            return {"session_id": session_id, "error": "no_events"}

        tokens_in = tokens_out = 0
        cost_usd = 0.0
        stages: List[Dict] = []
        models: Dict[str, int] = defaultdict(int)
        skills: Dict[str, int] = defaultdict(int)
        rfcs: List[str] = []
        specs: List[str] = []
        verif_pass = verif_fail = 0
        stage_starts: Dict[str, float] = {}
        start_ts = end_ts = None

        for ev in events:
            ts = ev.timestamp
            if start_ts is None or ts < start_ts:
                start_ts = ts
            if end_ts is None or ts > end_ts:
                end_ts = ts

            cat, etype, p = ev.category, ev.event_type, ev.payload

            if cat == "TOKENS":
                tokens_in  += p.get("input_tokens",  0)
                tokens_out += p.get("output_tokens", 0)

            elif cat == "COSTS":
                cost_usd += p.get("cost_usd", 0.0)

            elif cat == "MODELS":
                models[p.get("model_id", "unknown")] += 1

            elif cat == "SKILLS":
                skills[p.get("skill_name", "unknown")] += 1

            elif cat == "RFCS":
                rfc = p.get("rfc_id")
                if rfc and rfc not in rfcs:
                    rfcs.append(rfc)

            elif cat == "SPECS":
                spec = p.get("spec_id")
                if spec and spec not in specs:
                    specs.append(spec)

            elif cat == "EXECUTION":
                if etype == "StageStarted":
                    stage_starts[p.get("stage", "")] = ts
                elif etype == "StageCompleted":
                    stage = p.get("stage", "")
                    stages.append({
                        "stage": stage,
                        "duration_ms": round((ts - stage_starts.get(stage, ts)) * 1000),
                        "status": "completed",
                    })
                elif etype == "StageFailed":
                    stage = p.get("stage", "")
                    stages.append({
                        "stage": stage,
                        "duration_ms": round((ts - stage_starts.get(stage, ts)) * 1000),
                        "status": "failed",
                        "error": p.get("error", ""),
                    })

            elif cat == "VERIFICATION":
                if p.get("passed", False):
                    verif_pass += 1
                else:
                    verif_fail += 1

        duration_s = round(end_ts - start_ts, 2) if start_ts and end_ts else 0.0
        return {
            "session_id": session_id,
            "duration_seconds": duration_s,
            "tokens": {"input": tokens_in, "output": tokens_out,
                       "total": tokens_in + tokens_out},
            "cost_usd": round(cost_usd, 6),
            "stages": stages,
            "models": dict(models),
            "skills": dict(skills),
            "rfcs": rfcs,
            "specs": specs,
            "verification": {"passed": verif_pass, "failed": verif_fail},
            "event_count": len(events),
        }

    # ── workspace analytics ───────────────────────────────────────────────────

    def workspace_analytics(self, workspace_id: str) -> Dict[str, Any]:
        """Aggregate analytics for all sessions in a workspace."""
        all_events = [
            ev for ev in self.store.iter_all()
            if ev.workspace_id == workspace_id
        ]
        sessions = list({ev.session_id for ev in all_events if ev.session_id})
        total_tokens = sum(
            ev.payload.get("input_tokens", 0) + ev.payload.get("output_tokens", 0)
            for ev in all_events if ev.category == "TOKENS"
        )
        total_cost = sum(
            ev.payload.get("cost_usd", 0.0)
            for ev in all_events if ev.category == "COSTS"
        )
        model_usage: Dict[str, int] = defaultdict(int)
        skill_usage: Dict[str, int] = defaultdict(int)
        for ev in all_events:
            if ev.category == "MODELS":
                model_usage[ev.payload.get("model_id", "unknown")] += 1
            elif ev.category == "SKILLS":
                skill_usage[ev.payload.get("skill_name", "unknown")] += 1

        verif_pass = sum(
            1 for ev in all_events
            if ev.category == "VERIFICATION" and ev.payload.get("passed", False)
        )
        verif_fail = sum(
            1 for ev in all_events
            if ev.category == "VERIFICATION" and not ev.payload.get("passed", True)
        )

        return {
            "workspace_id": workspace_id,
            "total_sessions": len(sessions),
            "total_events": len(all_events),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "model_usage": dict(model_usage),
            "skill_usage": dict(skill_usage),
            "verification": {"passed": verif_pass, "failed": verif_fail},
        }

    # ── global analytics ──────────────────────────────────────────────────────

    def global_analytics(self) -> Dict[str, Any]:
        """Global analytics across the entire event store."""
        all_sessions = self.store.list_sessions()
        all_streams  = self.store.list_streams()
        total_events = self.store.total_count()
        total_tokens = sum(
            ev.payload.get("input_tokens", 0) + ev.payload.get("output_tokens", 0)
            for ev in self.store.iter_all() if ev.category == "TOKENS"
        )
        total_cost = sum(
            ev.payload.get("cost_usd", 0.0)
            for ev in self.store.iter_all() if ev.category == "COSTS"
        )
        return {
            "total_sessions": len(all_sessions),
            "total_streams": len(all_streams),
            "total_events": total_events,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "generated_at": time.time(),
        }

    # ── trend analytics ───────────────────────────────────────────────────────

    def cost_trend(self, last_n_sessions: int = 10) -> List[Dict[str, Any]]:
        """Cost per session for the last N sessions."""
        sessions = self.store.list_sessions()[-last_n_sessions:]
        trend = []
        for sid in sessions:
            events = self.store.read_session(sid)
            cost = sum(
                ev.payload.get("cost_usd", 0.0)
                for ev in events if ev.category == "COSTS"
            )
            ts = min((ev.timestamp for ev in events), default=0.0)
            trend.append({"session_id": sid, "cost_usd": round(cost, 6), "timestamp": ts})
        return sorted(trend, key=lambda x: x["timestamp"])

    def token_trend(self, last_n_sessions: int = 10) -> List[Dict[str, Any]]:
        """Token usage per session for the last N sessions."""
        sessions = self.store.list_sessions()[-last_n_sessions:]
        trend = []
        for sid in sessions:
            events = self.store.read_session(sid)
            tokens = sum(
                ev.payload.get("input_tokens", 0) + ev.payload.get("output_tokens", 0)
                for ev in events if ev.category == "TOKENS"
            )
            ts = min((ev.timestamp for ev in events), default=0.0)
            trend.append({"session_id": sid, "tokens": tokens, "timestamp": ts})
        return sorted(trend, key=lambda x: x["timestamp"])
