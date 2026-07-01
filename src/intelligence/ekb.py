import os
import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class EngineeringKnowledgeBase:
    """Central Object Versioned Memory Database for Aetheris (SPEC-007)."""
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()
        self.kb_dir = self.workspace_path / ".aetheris" / "kb"
        self.kb_dir.mkdir(parents=True, exist_ok=True)

    def _calculate_checksum(self, content: dict) -> str:
        serialized = json.dumps(content, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def register_object(self, obj_type: str, content: dict, producer: str = "Kernel") -> str:
        """Saves a schema-validated version-controlled knowledge object."""
        checksum = self._calculate_checksum(content)
        
        # Deduce object_id based on content or type
        obj_id = content.get("id") or content.get("object_id") or f"{obj_type}_{int(time.time() * 1000)}"
        
        # Check current version
        version = 1
        history_file = self.kb_dir / f"{obj_id}_history.json"
        history = []
        if history_file.exists():
            try:
                history = json.loads(history_file.read_text(encoding="utf-8"))
                version = len(history) + 1
            except Exception:
                pass

        obj_data = {
            "object_id": obj_id,
            "version": version,
            "type": obj_type,
            "producer": producer,
            "content": content,
            "validation": {
                "checksum": checksum,
                "verified": True,
                "timestamp": time.time()
            }
        }
        
        # Write object file
        obj_file = self.kb_dir / f"{obj_id}.json"
        obj_file.write_text(json.dumps(obj_data, indent=2), encoding="utf-8")
        
        # Write specific version file
        ver_file = self.kb_dir / f"{obj_id}_v{version}.json"
        ver_file.write_text(json.dumps(obj_data, indent=2), encoding="utf-8")

        # Update history registry
        history.append({
            "version": version,
            "checksum": checksum,
            "timestamp": obj_data["validation"]["timestamp"],
            "producer": producer
        })
        history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")

        return obj_id

    def get_object(self, obj_id: str, version: Optional[int] = None) -> Optional[dict]:
        """Fetches a specific object by ID and optional version constraint."""
        if version:
            target_file = self.kb_dir / f"{obj_id}_v{version}.json"
        else:
            target_file = self.kb_dir / f"{obj_id}.json"
            
        if not target_file.exists():
            return None
            
        try:
            data = json.loads(target_file.read_text(encoding="utf-8"))
            # Integrity check
            content = data.get("content", {})
            checksum = self._calculate_checksum(content)
            if data.get("validation", {}).get("checksum") != checksum:
                raise ValueError(f"Checksum verification failed for object: {obj_id}")
            return data
        except Exception:
            return None

    def query_objects(self, filters: dict) -> List[dict]:
        """Queries registered knowledge objects based on metadata tags or content matches."""
        results = []
        for f in self.kb_dir.glob("*.json"):
            # Exclude version-specific and history files to prevent duplicates
            if "_v" in f.name or "_history" in f.name:
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                match = True
                for k, v in filters.items():
                    # Handle queries against top-level metadata or nested content
                    if k in data and data[k] != v:
                        match = False
                        break
                    elif k not in data and data.get("content", {}).get(k) != v:
                        match = False
                        break
                if match:
                    results.append(data)
            except Exception:
                pass
        return results

    def purge_all(self) -> None:
        """Removes all stored database entities cleanly."""
        for f in self.kb_dir.glob("*.json"):
            try:
                f.unlink()
            except Exception:
                pass
