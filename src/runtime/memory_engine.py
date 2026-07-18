"""
MemoryEngine — Phase 4 Engineering Memory Synchronisation.

Syncs EKB state, session snapshots, and checkpoints across sessions.
Emits MEMORY category events to the EventStore for full auditability.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.event_store import EventStore


class MemoryEngine:
    """
    Manages persistent engineering memory:
    - EKB (Engineering Knowledge Base) entry tracking
    - Session snapshots for replay
    - Checkpoint management
    - Cross-session context transfer
    """

    def __init__(
        self,
        workspace_path: str,
        event_store: EventStore,
        session_id: str = "",
    ):
        self.workspace = Path(workspace_path).resolve()
        self.store = event_store
        self.session_id = session_id

        self._mem_dir = self.workspace / ".aetheris" / "memory"
        self._snap_dir = self._mem_dir / "snapshots"
        self._ckpt_dir = self._mem_dir / "checkpoints"
        for d in (self._mem_dir, self._snap_dir, self._ckpt_dir):
            d.mkdir(parents=True, exist_ok=True)

        self._ekb_count = self._count_ekb_entries()

    # ── EKB tracking ──────────────────────────────────────────────────────────

    def _count_ekb_entries(self) -> int:
        kb_dir = self.workspace / ".aetheris" / "kb"
        if not kb_dir.exists():
            return 0
        return sum(
            1 for f in kb_dir.glob("*.json")
            if "_v" not in f.name and "_history" not in f.name
        )

    def on_ekb_write(self, obj_id: str, obj_type: str):
        """Call after every EKB register_object() to track and emit events."""
        self._ekb_count = self._count_ekb_entries()
        self.store.emit(
            category="MEMORY",
            event_type="EKBEntryWritten",
            payload={"obj_id": obj_id, "obj_type": obj_type,
                     "total_entries": self._ekb_count},
            session_id=self.session_id,
        )

    # ── snapshots ─────────────────────────────────────────────────────────────

    def save_snapshot(self, label: str, data: Dict[str, Any]) -> str:
        """Persist a named memory snapshot for this session."""
        snap_id = f"{self.session_id}_{label}_{int(time.time())}"
        snap_path = self._snap_dir / f"{snap_id}.json"
        snap_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.store.emit(
            category="MEMORY",
            event_type="SnapshotSaved",
            payload={"snapshot_id": snap_id, "label": label,
                     "path": str(snap_path)},
            session_id=self.session_id,
        )
        return snap_id

    def load_snapshot(self, snap_id: str) -> Optional[Dict[str, Any]]:
        snap_path = self._snap_dir / f"{snap_id}.json"
        if not snap_path.exists():
            return None
        try:
            return json.loads(snap_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_snapshots(self) -> List[Dict[str, Any]]:
        result = []
        for f in sorted(self._snap_dir.glob("*.json"), key=lambda x: x.stat().st_mtime):
            result.append({"snapshot_id": f.stem, "path": str(f),
                           "modified": f.stat().st_mtime})
        return result

    # ── checkpoints ───────────────────────────────────────────────────────────

    def save_checkpoint(self, checkpoint_id: str, state: Dict[str, Any]):
        path = self._ckpt_dir / f"{checkpoint_id}.json"
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        self.store.emit(
            category="MEMORY",
            event_type="CheckpointSaved",
            payload={"checkpoint_id": checkpoint_id, "path": str(path)},
            session_id=self.session_id,
        )

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        path = self._ckpt_dir / f"{checkpoint_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_checkpoints(self) -> List[str]:
        return [f.stem for f in sorted(self._ckpt_dir.glob("*.json"))]

    # ── cross-session context ─────────────────────────────────────────────────

    def transfer_context(self, from_session_id: str) -> Dict[str, Any]:
        """Load the latest snapshot from a previous session for context continuity."""
        snapshots = [
            f for f in self._snap_dir.glob(f"{from_session_id}_*.json")
        ]
        if not snapshots:
            return {}
        latest = max(snapshots, key=lambda f: f.stat().st_mtime)
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            self.store.emit(
                category="MEMORY",
                event_type="ContextTransferred",
                payload={"from_session": from_session_id,
                         "snapshot": latest.stem},
                session_id=self.session_id,
            )
            return data
        except Exception:
            return {}

    @property
    def ekb_entry_count(self) -> int:
        return self._count_ekb_entries()
