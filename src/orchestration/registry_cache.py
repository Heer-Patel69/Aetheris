import os
import json
import hashlib
import time
import re
import sys
from pathlib import Path
from kernel.utils import is_safe_path

class RegistryCache:
    """
    Unified Skill Registry.
    Generates and maintains a metadata-only registry for all engineering capabilities.
    Indexes: Aetheris Skills, Headroom Skills, Claude Code Skills/Templates, RFCs, SPECs, and Integrations.
    """
    def __init__(self, workspace_path, cache_dir=None):
        self.workspace_path = Path(workspace_path).resolve()
        
        # Save registry file under .aetheris/runtime/
        self.aetheris_runtime_dir = self.workspace_path / ".aetheris" / "runtime"
        self.aetheris_runtime_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.aetheris_runtime_dir / "skill_registry.json"

        # Search roots
        self.roots = {
            "aetheris-skills": self.workspace_path / "skills",
            "global-skills": Path("~/.gemini/config/skills").expanduser().resolve(),
            "rfc-library": self.workspace_path / "rfcs",
            "integrations": self.workspace_path / "integrations"
        }

    def _get_file_hash(self, filepath):
        """Computes SHA-256 hash of file content."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _parse_metadata(self, filepath, source, relative_dir):
        """Parses frontmatter metadata and extracts structure while preserving NO CONTENT policy."""
        filepath = Path(filepath)
        filename = filepath.name
        stat = filepath.stat()
        file_hash = self._get_file_hash(filepath)

        # Basic/Default Metadata structure
        metadata = {
            "id": filepath.stem,
            "name": filepath.stem.replace("-", " ").title(),
            "source_repository": source,
            "parent_folder": str(relative_dir),
            "category": relative_dir.parts[0] if relative_dir.parts else "general",
            "subcategory": relative_dir.parts[1] if len(relative_dir.parts) > 1 else "",
            "description": "No description provided.",
            "tags": [],
            "keywords": [],
            "capabilities": [],
            "dependencies": [],
            "related_rfc": "",
            "related_spec": "",
            "supported_frameworks": [],
            "supported_languages": [],
            "complexity": "moderate",
            "version": "1.0.0",
            "author": "Aetheris Engine",
            "hash": file_hash,
            "last_updated": stat.st_mtime,
            "entry_point": str(filepath),
            "estimated_tokens": 1500,
            "estimated_runtime": 1.0
        }

        # Try to parse markdown / yaml frontmatter
        if filename.endswith(".md"):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Parse frontmatter
                if content.startswith("---"):
                    parts = content.split("---")
                    if len(parts) >= 3:
                        import yaml
                        fm = yaml.safe_load(parts[1]) or {}
                        
                        metadata["id"] = fm.get("id", metadata["id"])
                        metadata["name"] = fm.get("name", metadata["name"])
                        metadata["description"] = fm.get("description", metadata["description"])
                        metadata["version"] = fm.get("version", metadata["version"])
                        metadata["author"] = fm.get("author", metadata["author"])
                        metadata["complexity"] = fm.get("complexity", metadata["complexity"])
                        metadata["estimated_tokens"] = fm.get("estimated_context_tokens", fm.get("estimated_tokens", metadata["estimated_tokens"]))
                        metadata["estimated_runtime"] = fm.get("estimated_runtime", metadata["estimated_runtime"])
                        metadata["capabilities"] = fm.get("capabilities", [])
                        metadata["dependencies"] = fm.get("dependencies", [])
                        metadata["supported_languages"] = fm.get("languages", [])
                        metadata["supported_frameworks"] = fm.get("frameworks", [])
                        metadata["tags"] = fm.get("tags", [])
                        metadata["keywords"] = fm.get("keywords", [])
                        metadata["related_rfc"] = fm.get("related_rfc", "")
                        metadata["related_spec"] = fm.get("related_spec", "")
            except Exception:
                pass

        # Parse SPEC/RFC files specifically
        if filename.startswith("RFC-") or filename.startswith("SPEC-"):
            metadata["category"] = "rfc-spec"
            metadata["name"] = filename.replace(".md", "")
            metadata["capabilities"] = ["spec-audit" if filename.startswith("SPEC-") else "rfc-audit"]

        # Ensure NO CONTENT policy (Never store prompts, full instructions, body)
        return metadata

    def load_registry(self, force_rebuild=False):
        """Loads unified registry from json cache. If change is detected, rebuilds it."""
        if not force_rebuild and self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Simple validation of signatures to see if files changed
                    signatures = data.get("signatures", {})
                    changed = False
                    for path, cached_hash in signatures.items():
                        if not os.path.exists(path) or self._get_file_hash(path) != cached_hash:
                            changed = True
                            break
                    if not changed:
                        return data.get("skills", {})
            except Exception:
                pass

        # Rebuild registry
        print("[Registry] Building Unified Skill Registry...")
        skills = {}
        signatures = {}

        for source, root_path in self.roots.items():
            if not root_path.exists():
                continue
                
            for root, dirs, files in os.walk(root_path):
                # Calculate path relative to root
                relative_root = Path(root).relative_to(root_path)
                
                for file in files:
                    # Index md, yaml, json files
                    if file.endswith((".md", ".json", ".yaml")):
                        filepath = os.path.join(root, file)
                        # Avoid scanning the .aetheris directory itself if it is inside roots
                        if ".aetheris" in filepath:
                            continue
                            
                        metadata = self._parse_metadata(filepath, source, relative_root)
                        skills[metadata["id"]] = metadata
                        signatures[filepath] = metadata["hash"]

        # Save registry
        registry_data = {
            "skills": skills,
            "signatures": signatures,
            "last_updated": time.time()
        }
        
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2)

        print(f"[Registry] Unified Registry rebuilt successfully. {len(skills)} entries indexed.")
        return skills

    def find_by_capability(self, registry, capability):
        """Resolves skills matching the requested capability query."""
        matches = []
        cap_lower = capability.lower()
        
        for skill_id, skill in registry.items():
            score = 0
            if cap_lower in skill["name"].lower():
                score += 30
            if any(cap_lower == lang.lower() for lang in skill.get("supported_languages", [])):
                score += 50
            if any(cap_lower == fw.lower() for fw in skill.get("supported_frameworks", [])):
                score += 50
            if any(cap_lower == cap.lower() for cap in skill.get("capabilities", [])):
                score += 40
            if any(cap_lower == kw.lower() for kw in skill.get("keywords", [])):
                score += 20
            if cap_lower in skill.get("description", "").lower():
                score += 10
                
            if score > 0:
                skill_copy = skill.copy()
                skill_copy["match_score"] = score
                matches.append(skill_copy)
                
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

if __name__ == "__main__":
    cache = RegistryCache(".")
    reg = cache.load_registry(force_rebuild=True)