"""
ProjectionEngine — Real-time state projections from the EventStore (Phase 4).

Every dashboard widget subscribes to a named projection rather than querying
raw events. Projections are rebuilt incrementally as new events arrive.
"""
import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from runtime.event_store import EngEvent, EventStore


class Projection:
    """A named, incrementally-maintained read model derived from events."""

    def __init__(self, name: str):
        self.name = name
        self._data: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._version = 0
        self._updated_at: float = 0.0
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []

    def update(self, delta: Dict[str, Any]):
        with self._lock:
            self._data.update(delta)
            self._version += 1
            self._updated_at = time.time()
        for cb in list(self._subscribers):
            try:
                cb(self.snapshot())
            except Exception:
                pass

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "projection": self.name,
                "version": self._version,
                "updated_at": self._updated_at,
                "data": dict(self._data),
            }

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        if callback in self._subscribers:
            self._subscribers.remove(callback)


class ProjectionEngine:
    """
    Maintains all live projections and routes incoming events to them.

    Built-in projections
    --------------------
    executive_overview  – high-level system health
    runtime_inspector   – active session / engine steps
    token_analytics     – token/cost counters
    model_analytics     – per-model usage stats
    skill_analytics     – skill invocation counts
    verification_center – DoD gate results
    memory_analytics    – EKB entry counts
    engineering_insights– optimization signal stream
    """

    def __init__(self, event_store: EventStore):
        self._store = event_store
        self._projections: Dict[str, Projection] = {}
        self._init_projections()
        # subscribe to live events
        event_store.subscribe(self._on_event)
        # rebuild from history
        self._rebuild_from_history()

    # ── init projections ──────────────────────────────────────────────────────

    def _init_projections(self):
        names = [
            "executive_overview",
            "runtime_inspector",
            "token_analytics",
            "model_analytics",
            "skill_analytics",
            "rfc_analytics",
            "spec_analytics",
            "cost_analytics",
            "verification_center",
            "review_center",
            "memory_analytics",
            "observability",
            "engineering_insights",
            "project_health",
            "repository_explorer",
            "engineering_timeline",
        ]
        for name in names:
            self._projections[name] = Projection(name)

        # seed defaults
        self._projections["executive_overview"].update({
            "sessions_total": 0, "sessions_active": 0,
            "executions_total": 0, "executions_running": 0,
            "skills_loaded": 0, "errors_total": 0,
            "system_status": "idle",
        })
        self._projections["token_analytics"].update({
            "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
            "sessions_by_token": {},
        })
        self._projections["cost_analytics"].update({
            "total_cost_usd": 0.0, "session_costs": {},
            "model_costs": {}, "budget_usd": 5.0, "budget_remaining_usd": 5.0,
        })
        self._projections["model_analytics"].update({"models": {}})
        self._projections["skill_analytics"].update({"skills": {}})
        self._projections["rfc_analytics"].update({"rfcs": {}})
        self._projections["spec_analytics"].update({"specs": {}})
        self._projections["verification_center"].update({
            "gates_passed": 0, "gates_failed": 0, "recent": [],
        })
        self._projections["memory_analytics"].update({
            "ekb_entries": 0, "memory_ops": [], "checkpoints": 0,
        })

    # ── event router ──────────────────────────────────────────────────────────

    def _on_event(self, event: EngEvent):
        cat   = event.category
        etype = event.event_type
        p     = event.payload
        sid   = event.session_id

        if cat == "SESSION":
            ov = self._projections["executive_overview"]
            data = ov._data
            if etype == "SessionStarted":
                ov.update({
                    "sessions_total": data.get("sessions_total", 0) + 1,
                    "sessions_active": data.get("sessions_active", 0) + 1,
                    "system_status": "running",
                    "active_session": sid,
                })
            elif etype in ("SessionCompleted", "SessionFailed"):
                ov.update({
                    "sessions_active": max(0, data.get("sessions_active", 1) - 1),
                    "system_status": "idle",
                })

        elif cat == "EXECUTION":
            ri = self._projections["runtime_inspector"]
            ov = self._projections["executive_overview"]
            if etype == "StageStarted":
                ri.update({
                    "active_stage": p.get("stage"),
                    "active_session": sid,
                    "stage_started_at": event.timestamp,
                })
                ov.update({"executions_running": max(1, ov._data.get("executions_running", 0))})
            elif etype == "StageCompleted":
                ri.update({
                    "last_completed_stage": p.get("stage"),
                    "last_stage_duration_ms": p.get("duration_ms", 0),
                })
                ov.update({"executions_total": ov._data.get("executions_total", 0) + 1})
            elif etype == "StageFailed":
                ri.update({"last_error": p.get("error"), "last_failed_stage": p.get("stage")})
                ov.update({"errors_total": ov._data.get("errors_total", 0) + 1})

        elif cat == "TOKENS":
            ta = self._projections["token_analytics"]
            inp = p.get("input_tokens", 0)
            out = p.get("output_tokens", 0)
            ta.update({
                "input_tokens":  ta._data.get("input_tokens",  0) + inp,
                "output_tokens": ta._data.get("output_tokens", 0) + out,
                "total_tokens":  ta._data.get("total_tokens",  0) + inp + out,
            })

        elif cat == "COSTS":
            ca = self._projections["cost_analytics"]
            cost = p.get("cost_usd", 0.0)
            total = ca._data.get("total_cost_usd", 0.0) + cost
            budget = ca._data.get("budget_usd", 5.0)
            model_costs = dict(ca._data.get("model_costs", {}))
            model_id = p.get("model_id", "unknown")
            model_costs[model_id] = model_costs.get(model_id, 0.0) + cost
            ca.update({
                "total_cost_usd": round(total, 6),
                "budget_remaining_usd": round(max(0.0, budget - total), 6),
                "model_costs": model_costs,
            })

        elif cat == "MODELS":
            ma = self._projections["model_analytics"]
            models = dict(ma._data.get("models", {}))
            mid = p.get("model_id", "unknown")
            entry = models.get(mid, {"calls": 0, "provider": p.get("provider", "")})
            entry["calls"] += 1
            models[mid] = entry
            ma.update({"models": models})

        elif cat == "SKILLS":
            sa = self._projections["skill_analytics"]
            skills = dict(sa._data.get("skills", {}))
            skill = p.get("skill_name", "unknown")
            skills[skill] = skills.get(skill, 0) + 1
            sa.update({"skills": skills})
            ov = self._projections["executive_overview"]
            ov.update({"skills_loaded": len(skills)})

        elif cat == "RFCS":
            ra = self._projections["rfc_analytics"]
            rfcs = dict(ra._data.get("rfcs", {}))
            rfc = p.get("rfc_id", "unknown")
            rfcs[rfc] = rfcs.get(rfc, 0) + 1
            ra.update({"rfcs": rfcs})

        elif cat == "SPECS":
            sa = self._projections["spec_analytics"]
            specs = dict(sa._data.get("specs", {}))
            spec = p.get("spec_id", "unknown")
            specs[spec] = specs.get(spec, 0) + 1
            sa.update({"specs": specs})

        elif cat == "VERIFICATION":
            vc = self._projections["verification_center"]
            passed = p.get("passed", False)
            recent = list(vc._data.get("recent", []))
            recent.append({"gate": p.get("gate"), "passed": passed,
                           "timestamp": event.timestamp})
            recent = recent[-50:]  # keep last 50
            vc.update({
                "gates_passed": vc._data.get("gates_passed", 0) + (1 if passed else 0),
                "gates_failed": vc._data.get("gates_failed", 0) + (0 if passed else 1),
                "recent": recent,
            })

        elif cat == "MEMORY":
            me = self._projections["memory_analytics"]
            ops = list(me._data.get("memory_ops", []))
            ops.append({"op": etype, "timestamp": event.timestamp, **p})
            ops = ops[-100:]
            delta: Dict[str, Any] = {"memory_ops": ops}
            if etype == "EKBEntryWritten":
                delta["ekb_entries"] = me._data.get("ekb_entries", 0) + 1
            elif etype == "CheckpointSaved":
                delta["checkpoints"] = me._data.get("checkpoints", 0) + 1
            me.update(delta)

        elif cat == "INSIGHT":
            ei = self._projections["engineering_insights"]
            insights = list(ei._data.get("insights", []))
            insights.append({"type": etype, "payload": p, "timestamp": event.timestamp})
            insights = insights[-200:]
            ei.update({"insights": insights})

        # engineering timeline — append every event
        tl = self._projections["engineering_timeline"]
        events_list = list(tl._data.get("events", []))
        events_list.append({
            "seq": event.sequence, "ts": event.timestamp,
            "cat": cat, "type": etype, "session": sid,
        })
        events_list = events_list[-500:]
        tl.update({"events": events_list, "total_events": self._store.total_count()})

    # ── rebuild from history ──────────────────────────────────────────────────

    def _rebuild_from_history(self):
        for event in self._store.iter_all():
            self._on_event(event)

    # ── public API ────────────────────────────────────────────────────────────

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        proj = self._projections.get(name)
        return proj.snapshot() if proj else None

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        return {name: p.snapshot() for name, p in self._projections.items()}

    def subscribe(self, projection_name: str, callback: Callable[[Dict[str, Any]], None]):
        proj = self._projections.get(projection_name)
        if proj:
            proj.subscribe(callback)

    def unsubscribe(self, projection_name: str, callback: Callable[[Dict[str, Any]], None]):
        proj = self._projections.get(projection_name)
        if proj:
            proj.unsubscribe(callback)

    def list_projections(self) -> List[str]:
        return list(self._projections.keys())
