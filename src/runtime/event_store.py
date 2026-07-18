"""
EventStore — Immutable Append-Only Engineering Event Store (Phase 4)

Every runtime action emits an immutable event persisted here.
Supports full event sourcing, replay, and projection rebuilding.
"""

import json
import time
import uuid
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Iterator


# ─── Event Schema ─────────────────────────────────────────────────────────────

EVENT_CATEGORIES = {
    "SESSION",
    "WORKSPACE",
    "PROJECT",
    "EXECUTION",
    "DECISION",
    "FILES",
    "TELEMETRY",
    "TOKENS",
    "COSTS",
    "MODELS",
    "SKILLS",
    "RFCS",
    "SPECS",
    "VERIFICATION",
    "REVIEW",
    "REPLAY",
    "MEMORY",
    "OPTIMIZATION",
    "INSIGHT",
}


class EngEvent:
    """Immutable engineering event record."""

    __slots__ = (
        "event_id",
        "stream_id",
        "category",
        "event_type",
        "payload",
        "timestamp",
        "sequence",
        "session_id",
        "workspace_id",
        "causation_id",
    )

    def __init__(
        self,
        category: str,
        event_type: str,
        payload: Dict[str, Any],
        stream_id: str = "global",
        session_id: str = "",
        workspace_id: str = "",
        causation_id: str = "",
        sequence: int = 0,
    ):
        self.event_id = str(uuid.uuid4())
        self.stream_id = stream_id
        self.category = category
        self.event_type = event_type
        self.payload = payload
        self.timestamp = time.time()
        self.sequence = sequence
        self.session_id = session_id
        self.workspace_id = workspace_id
        self.causation_id = causation_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "stream_id": self.stream_id,
            "category": self.category,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "session_id": self.session_id,
            "workspace_id": self.workspace_id,
            "causation_id": self.causation_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EngEvent":
        ev = cls.__new__(cls)
        ev.event_id = d["event_id"]
        ev.stream_id = d.get("stream_id", "global")
        ev.category = d["category"]
        ev.event_type = d["event_type"]
        ev.payload = d.get("payload", {})
        ev.timestamp = d.get("timestamp", 0.0)
        ev.sequence = d.get("sequence", 0)
        ev.session_id = d.get("session_id", "")
        ev.workspace_id = d.get("workspace_id", "")
        ev.causation_id = d.get("causation_id", "")
        return ev


# ─── EventStore ───────────────────────────────────────────────────────────────

class EventStore:
    """
    Immutable append-only event store.

    Layout on disk:
        <store_dir>/
            global.events.jsonl       — all events in order
            streams/<stream_id>.jsonl — per-stream partition
            index/by_session/<session_id>.idx  — index files (newline list of offsets)
            meta.json                 — store metadata
    """

    def __init__(self, store_dir: str):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        (self.store_dir / "streams").mkdir(exist_ok=True)
        (self.store_dir / "index").mkdir(exist_ok=True)
        (self.store_dir / "index" / "by_session").mkdir(exist_ok=True)
        (self.store_dir / "index" / "by_category").mkdir(exist_ok=True)

        self._lock = threading.Lock()
        self._sequence = self._load_sequence()
        self._subscribers: List[Callable[[EngEvent], None]] = []

    # ── sequence ──────────────────────────────────────────────────────────────

    def _load_sequence(self) -> int:
        meta_path = self.store_dir / "meta.json"
        if meta_path.exists():
            try:
                return json.loads(meta_path.read_text())["sequence"]
            except Exception:
                pass
        return 0

    def _save_sequence(self):
        (self.store_dir / "meta.json").write_text(
            json.dumps({"sequence": self._sequence, "updated_at": time.time()}),
            encoding="utf-8",
        )

    # ── append ────────────────────────────────────────────────────────────────

    def append(self, event: EngEvent) -> EngEvent:
        """Append an immutable event to the store. Thread-safe."""
        with self._lock:
            self._sequence += 1
            event.sequence = self._sequence
            line = json.dumps(event.to_dict(), ensure_ascii=False) + "\n"

            # global log
            global_log = self.store_dir / "global.events.jsonl"
            with open(global_log, "a", encoding="utf-8") as f:
                f.write(line)

            # per-stream partition
            stream_log = self.store_dir / "streams" / f"{event.stream_id}.jsonl"
            with open(stream_log, "a", encoding="utf-8") as f:
                f.write(line)

            # session index
            if event.session_id:
                idx = self.store_dir / "index" / "by_session" / f"{event.session_id}.idx"
                with open(idx, "a", encoding="utf-8") as f:
                    f.write(f"{event.event_id}\n")

            # category index
            cat_idx = self.store_dir / "index" / "by_category" / f"{event.category}.idx"
            with open(cat_idx, "a", encoding="utf-8") as f:
                f.write(f"{event.event_id}\n")

            self._save_sequence()

        # notify subscribers outside lock
        for cb in list(self._subscribers):
            try:
                cb(event)
            except Exception:
                pass

        return event

    # ── emit convenience ──────────────────────────────────────────────────────

    def emit(
        self,
        category: str,
        event_type: str,
        payload: Dict[str, Any],
        stream_id: str = "global",
        session_id: str = "",
        workspace_id: str = "",
        causation_id: str = "",
    ) -> EngEvent:
        ev = EngEvent(
            category=category,
            event_type=event_type,
            payload=payload,
            stream_id=stream_id,
            session_id=session_id,
            workspace_id=workspace_id,
            causation_id=causation_id,
        )
        return self.append(ev)

    # ── subscribe ─────────────────────────────────────────────────────────────

    def subscribe(self, callback: Callable[[EngEvent], None]):
        """Register a live callback fired on every new event."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[EngEvent], None]):
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    # ── read ──────────────────────────────────────────────────────────────────

    def iter_all(self, from_sequence: int = 0) -> Iterator[EngEvent]:
        """Stream all events from global log in order."""
        global_log = self.store_dir / "global.events.jsonl"
        if not global_log.exists():
            return
        with open(global_log, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    if d.get("sequence", 0) >= from_sequence:
                        yield EngEvent.from_dict(d)
                except Exception:
                    pass

    def read_stream(self, stream_id: str, from_sequence: int = 0) -> List[EngEvent]:
        """Read all events from a specific stream."""
        path = self.store_dir / "streams" / f"{stream_id}.jsonl"
        if not path.exists():
            return []
        results = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    if d.get("sequence", 0) >= from_sequence:
                        results.append(EngEvent.from_dict(d))
                except Exception:
                    pass
        return results

    def read_session(self, session_id: str) -> List[EngEvent]:
        """Read all events for a session (via index)."""
        idx = self.store_dir / "index" / "by_session" / f"{session_id}.idx"
        if not idx.exists():
            return []
        event_ids = set(idx.read_text(encoding="utf-8").splitlines())
        return [
            ev for ev in self.iter_all()
            if ev.event_id in event_ids
        ]

    def read_by_category(self, category: str, limit: int = 1000) -> List[EngEvent]:
        """Read events by category via index."""
        cat_idx = self.store_dir / "index" / "by_category" / f"{category}.idx"
        if not cat_idx.exists():
            return []
        event_ids = set(cat_idx.read_text(encoding="utf-8").splitlines()[-limit:])
        return [
            ev for ev in self.iter_all()
            if ev.event_id in event_ids
        ]

    def latest(self, n: int = 50) -> List[EngEvent]:
        """Return the N most recent events."""
        all_events = list(self.iter_all())
        return all_events[-n:] if len(all_events) > n else all_events

    def total_count(self) -> int:
        return self._sequence

    def list_streams(self) -> List[str]:
        return [p.stem for p in (self.store_dir / "streams").glob("*.jsonl")]

    def list_sessions(self) -> List[str]:
        return [
            p.stem
            for p in (self.store_dir / "index" / "by_session").glob("*.idx")
        ]
