import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

class StateEngine:
    """
    Git-like State Directory Engine managing the hierarchical layout under `.aetheris/`.
    Represents the unified state representation of the hypervisor.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_root = Path(workspace_path).resolve()
        self.aetheris_dir = self.workspace_root / ".aetheris"
        
        # Define all standard state subdirectories matching AEKS v1.0
        self.subdirs = {
            "config": self.aetheris_dir / "config",
            "state": self.aetheris_dir / "state",
            "memory": self.aetheris_dir / "memory",
            "graphs": self.aetheris_dir / "graphs",
            "artifacts": self.aetheris_dir / "artifacts",
            "logs": self.aetheris_dir / "logs",
            "providers": self.aetheris_dir / "providers",
            "skills": self.aetheris_dir / "skills",
            "rfcs": self.aetheris_dir / "rfcs",
            "specs": self.aetheris_dir / "specs",
            "benchmarks": self.aetheris_dir / "benchmarks",
            "analytics": self.aetheris_dir / "analytics",
            "history": self.aetheris_dir / "history",
            "snapshots": self.aetheris_dir / "snapshots",
            "cache": self.aetheris_dir / "cache",
            "checkpoints": self.aetheris_dir / "checkpoints",
            "reports": self.aetheris_dir / "reports"
        }

    def initialize(self) -> None:
        """Bootstraps the hierarchical `.aetheris/` directory structure."""
        self.aetheris_dir.mkdir(parents=True, exist_ok=True)
        for subdir_path in self.subdirs.values():
            subdir_path.mkdir(parents=True, exist_ok=True)
            
        # Write default metadata file if missing
        state_meta = self.subdirs["state"] / "metadata.json"
        if not state_meta.exists():
            meta = {
                "initialized_at": time.time(),
                "aeks_version": "1.0",
                "hypervisor_status": "idle"
            }
            state_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def save_checkpoint(self, checkpoint_id: str, data: Dict[str, Any]) -> None:
        """Saves a workflow checkpoint for scheduler recovery/rollback."""
        target = self.subdirs["checkpoints"] / f"{checkpoint_id}.json"
        target.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Loads a workflow checkpoint by identifier."""
        target = self.subdirs["checkpoints"] / f"{checkpoint_id}.json"
        if not target.exists():
            return {}
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_graph(self, name: str, graph_data: Dict[str, Any]) -> None:
        """Saves a queryable subgraph (e.g. technology, dependency, skill) under graphs."""
        target = self.subdirs["graphs"] / f"{name}.graph.json"
        target.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")

    def load_graph(self, name: str) -> Dict[str, Any]:
        """Loads a queryable subgraph from graphs."""
        target = self.subdirs["graphs"] / f"{name}.graph.json"
        if not target.exists():
            return {}
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_artifact(self, name: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Registers and version-controls a managed artifact with metadata and checksums."""
        checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
        artifact_path = self.subdirs["artifacts"] / name
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(content, encoding="utf-8")
        
        meta = {
            "checksum": checksum,
            "version": 1,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        meta_path = self.subdirs["artifacts"] / f"{name}.meta.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return artifact_path

    def load_artifact(self, name: str) -> Optional[str]:
        """Loads artifact content."""
        artifact_path = self.subdirs["artifacts"] / name
        if not artifact_path.exists():
            return None
        return artifact_path.read_text(encoding="utf-8")
        
    def get_artifact_meta(self, name: str) -> Dict[str, Any]:
        """Loads artifact metadata."""
        meta_path = self.subdirs["artifacts"] / f"{name}.meta.json"
        if not meta_path.exists():
            return {}
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
