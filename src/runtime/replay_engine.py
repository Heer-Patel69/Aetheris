"""
ReplayEngine — Engineering Execution Replay (Phase 4)

Reconstructs any past execution from the EventStore timeline.
Supports full replay, partial replay from a checkpoint, and diff between two sessions.
"""

import time
from typing import Any, Dict, List, Optional

from runtime.event_store import EventStore, EngEvent


# ─── Timeline ─────────────────────────────────────────────────────────────────

EXECUTION_TIMELINE_STAGES = [
    "Prompt",
    "Discovery",
    "Planning",
    "Architecture",
    "Skills",
    "RFC",
    "SPEC",
    "Models",
    "Implementation",
    "Verification",
    "Review",
    "Completion",
]


class ExecutionTimeline:
    """Ordered timeline of engineering stages reconstructed from events."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.stages: List[Dict[str, Any]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.files_touched: List[str] = []
        self.models_used: List[Dict[str, Any]] = []
        self.skills_loaded: List[str] = []
        self.rfcs_used: List[str] = []
        self.specs_used: List[str] = []
        self.tokens: Dict[str, int] = {"input": 0, "output": 0, "total": 0}
        self.cost_usd: float = 0.0
        self.verification_results: List[Dict[str, Any]] = []
        self.review_results: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.status: str = "unknown"

    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return round(self.end_time - self.start_time, 2)
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds(),
            "stages": self.stages,
            "decisions": self.decisions,
            "files_touched": self.files_touched,
            "models_used": self.models_used,
            "skills_loaded": self.skills_loaded,
            "rfcs_used": self.rfcs_used,
            "specs_used": self.specs_used,
            "tokens": self.tokens,
            "cost_usd": self.cost_usd,
            "verification_results": self.verification_results,
            "review_results": self.review_results,
        }


# ─── ReplayEngine ─────────────────────────────────────────────────────────────

class ReplayEngine:
    """
    Reconstructs past executions from the EventStore.

    Usage:
        replay = ReplayEngine(event_store)
        timeline = replay.reconstruct_session("sess-abc123")
        frame = replay.step_to_stage("sess-abc123", "Implementation")
    """

    def __init__(self, event_store: EventStore):
        self.store = event_store

    # ── full session reconstruction ───────────────────────────────────────────

    def reconstruct_session(self, session_id: str) -> ExecutionTimeline:
        """Rebuild the complete execution timeline for a session from its events."""
        events = self.store.read_session(session_id)
        return self._build_timeline(session_id, events)

    def reconstruct_from_sequence(
        self, session_id: str, from_seq: int, to_seq: int
    ) -> ExecutionTimeline:
        """Partial replay between two sequence numbers."""
        all_events = [
            ev
            for ev in self.store.iter_all(from_sequence=from_seq)
            if ev.session_id == session_id and ev.sequence <= to_seq
        ]
        return self._build_timeline(session_id, all_events)

    def step_to_stage(self, session_id: str, stage_name: str) -> ExecutionTimeline:
        """Replay up to (and including) the given stage."""
        events = self.store.read_session(session_id)
        cutoff = None
        for ev in events:
            if (
                ev.category == "EXECUTION"
                and ev.event_type == "StageCompleted"
                and ev.payload.get("stage") == stage_name
            ):
                cutoff = ev.sequence
                break

        if cutoff is None:
            # stage not reached yet — replay what we have
            return self._build_timeline(session_id, events)

        filtered = [ev for ev in events if ev.sequence <= cutoff]
        return self._build_timeline(session_id, filtered)

    # ── diff ──────────────────────────────────────────────────────────────────

    def diff_sessions(
        self, session_a: str, session_b: str
    ) -> Dict[str, Any]:
        """Compare two execution timelines and surface differences."""
        tl_a = self.reconstruct_session(session_a)
        tl_b = self.reconstruct_session(session_b)

        stages_a = {s["name"] for s in tl_a.stages}
        stages_b = {s["name"] for s in tl_b.stages}

        return {
            "session_a": session_a,
            "session_b": session_b,
            "duration_delta_seconds": tl_b.duration_seconds() - tl_a.duration_seconds(),
            "token_delta": {
                k: tl_b.tokens.get(k, 0) - tl_a.tokens.get(k, 0)
                for k in ("input", "output", "total")
            },
            "cost_delta_usd": round(tl_b.cost_usd - tl_a.cost_usd, 6),
            "stages_only_in_a": sorted(stages_a - stages_b),
            "stages_only_in_b": sorted(stages_b - stages_a),
            "shared_stages": sorted(stages_a & stages_b),
            "files_added_in_b": sorted(
                set(tl_b.files_touched) - set(tl_a.files_touched)
            ),
            "files_removed_in_b": sorted(
                set(tl_a.files_touched) - set(tl_b.files_touched)
            ),
        }

    # ── list sessions ─────────────────────────────────────────────────────────

    def list_replayable_sessions(self) -> List[Dict[str, Any]]:
        """Return summary of all sessions available for replay."""
        sessions = self.store.list_sessions()
        summaries = []
        for sid in sessions:
            events = self.store.read_session(sid)
            if not events:
                continue
            tl = self._build_timeline(sid, events)
            summaries.append(
                {
                    "session_id": sid,
                    "status": tl.status,
                    "start_time": tl.start_time,
                    "duration_seconds": tl.duration_seconds(),
                    "stage_count": len(tl.stages),
                    "tokens_total": tl.tokens.get("total", 0),
                    "cost_usd": tl.cost_usd,
                }
            )
        summaries.sort(key=lambda x: x.get("start_time") or 0, reverse=True)
        return summaries

    # ── internal builder ──────────────────────────────────────────────────────

    def _build_timeline(
        self, session_id: str, events: List[EngEvent]
    ) -> ExecutionTimeline:
        tl = ExecutionTimeline(session_id)
        stage_starts: Dict[str, float] = {}

        for ev in events:
            ts = ev.timestamp
            p = ev.payload

            # bookend times
            if tl.start_time is None or ts < tl.start_time:
                tl.start_time = ts
            if tl.end_time is None or ts > tl.end_time:
                tl.end_time = ts

            cat = ev.category
            etype = ev.event_type

            if cat == "EXECUTION":
                if etype == "StageStarted":
                    stage_starts[p.get("stage", "")] = ts
                elif etype == "StageCompleted":
                    stage = p.get("stage", "")
                    started = stage_starts.get(stage, ts)
                    tl.stages.append(
                        {
                            "name": stage,
                            "started_at": started,
                            "completed_at": ts,
                            "duration_ms": round((ts - started) * 1000),
                            "status": "completed",
                            "metadata": p.get("metadata", {}),
                        }
                    )
                elif etype == "StageFailed":
                    stage = p.get("stage", "")
                    started = stage_starts.get(stage, ts)
                    tl.stages.append(
                        {
                            "name": stage,
                            "started_at": started,
                            "failed_at": ts,
                            "duration_ms": round((ts - started) * 1000),
                            "status": "failed",
                            "error": p.get("error", ""),
                        }
                    )
                elif etype == "SessionStarted":
                    tl.status = "running"
                elif etype in ("SessionCompleted", "SessionFinished"):
                    tl.status = "completed"
                elif etype == "SessionFailed":
                    tl.status = "failed"

            elif cat == "DECISION":
                tl.decisions.append(
                    {
                        "timestamp": ts,
                        "decision": p.get("decision", ""),
                        "rationale": p.get("rationale", ""),
                        "confidence": p.get("confidence", 1.0),
                    }
                )

            elif cat == "FILES":
                path = p.get("path", "")
                if path and path not in tl.files_touched:
                    tl.files_touched.append(path)

            elif cat == "MODELS":
                tl.models_used.append(
                    {
                        "timestamp": ts,
                        "model_id": p.get("model_id", ""),
                        "provider": p.get("provider", ""),
                        "task": p.get("task", ""),
                    }
                )

            elif cat == "SKILLS":
                skill = p.get("skill_name", "")
                if skill and skill not in tl.skills_loaded:
                    tl.skills_loaded.append(skill)

            elif cat == "RFCS":
                rfc = p.get("rfc_id", "")
                if rfc and rfc not in tl.rfcs_used:
                    tl.rfcs_used.append(rfc)

            elif cat == "SPECS":
                spec = p.get("spec_id", "")
                if spec and spec not in tl.specs_used:
                    tl.specs_used.append(spec)

            elif cat == "TOKENS":
                tl.tokens["input"] += p.get("input_tokens", 0)
                tl.tokens["output"] += p.get("output_tokens", 0)
                tl.tokens["total"] += p.get("total_tokens", 0)

            elif cat == "COSTS":
                tl.cost_usd += p.get("cost_usd", 0.0)

            elif cat == "VERIFICATION":
                tl.verification_results.append(
                    {
                        "timestamp": ts,
                        "gate": p.get("gate", ""),
                        "passed": p.get("passed", False),
                        "details": p.get("details", {}),
                    }
                )

            elif cat == "REVIEW":
                tl.review_results.append(
                    {
                        "timestamp": ts,
                        "reviewer": p.get("reviewer", ""),
                        "verdict": p.get("verdict", ""),
                        "comments": p.get("comments", ""),
                    }
                )

        if tl.status == "running" and tl.stages:
            tl.status = "partial"
        elif tl.status == "unknown" and tl.start_time:
            tl.status = "partial"

        tl.cost_usd = round(tl.cost_usd, 6)
        tl.tokens["total"] = tl.tokens["input"] + tl.tokens["output"]

        return tl
