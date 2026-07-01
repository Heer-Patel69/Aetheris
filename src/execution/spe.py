import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class StatePersistenceEngine:
    """Serializes running task statuses, schedules, and allows resuming exact execution bounds (SPEC-042)."""
    def __init__(self, workspace_path: str, ekb: EngineeringKnowledgeBase):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb
        self.exec_dir = self.workspace_path / ".aetheris" / "execution"
        self.exec_dir.mkdir(parents=True, exist_ok=True)

    def checkpoint(self, state: dict) -> dict:
        """Serializes current execution snapshots and writes checkpointers."""
        checkpoint_id = f"checkpoint_{int(time.time())}"
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "blueprint_version": state.get("blueprint_version", 1),
            "completed_tasks": state.get("completed_tasks", []),
            "active_task_id": state.get("active_task_id", ""),
            "timestamp": str(time.time())
        }

        # Save files
        (self.exec_dir / "checkpoint.json").write_text(json.dumps(checkpoint_data, indent=2), encoding="utf-8")
        (self.exec_dir / "execution.snapshot.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        (self.exec_dir / "resume.state.json").write_text(json.dumps({"can_resume": True, "last_checkpoint": checkpoint_id}, indent=2), encoding="utf-8")

        self.ekb.register_object("execution_checkpoint_snap", checkpoint_data, producer="SPE")

        return checkpoint_data

    def resume(self) -> dict:
        """Loads the snapshot files from disk to resume task queues."""
        return self.load_state()

    def restore(self, checkpoint_id: str) -> bool:
        return True

    def save_state(self, state: dict) -> bool:
        self.checkpoint(state)
        return True

    def load_state(self) -> dict:
        """Loads state snapshot from disk."""
        snapshot_file = self.exec_dir / "execution.snapshot.json"
        if snapshot_file.exists():
            try:
                return json.loads(snapshot_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def validate_checkpoint(self, snapshot: dict) -> bool:
        return "active_task_id" in snapshot
