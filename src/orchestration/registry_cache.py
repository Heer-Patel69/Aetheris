import json
import time
import sys
from pathlib import Path
from kernel.utils import is_safe_path
from orchestration.skill_scanner import SkillScanner
from orchestration.skill_parser import SkillParser

class RegistryCache:
    def __init__(self, workspace_path, cache_dir=None):
        self.workspace_path = Path(workspace_path).resolve()
        
        if cache_dir:
            self.cache_dir = Path(cache_dir).resolve()
        else:
            self.cache_dir = Path("~/.aetheris/cache").expanduser()
            
        if is_safe_path(self.cache_dir):
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
        self.cache_file = self.cache_dir / "registry.json"
        
        self.scanner = SkillScanner()
        self.parser = SkillParser()

    def _load_cache_file(self):
        """
        Safely load registry.json, catching parsing and corruption errors.
        """
        if not self.cache_file.exists():
            return None
            
        if not is_safe_path(self.cache_file):
            raise PermissionError(f"Security Boundary Violation: Path {self.cache_file} is out of bounds.")
            
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            sys.stderr.write(f"RegistryCache Warning: Cache file corrupted. Rebuilding. Error: {e}\n")
            try:
                self.cache_file.unlink()
            except Exception:
                pass
            return None

    def _save_cache_file(self, cache_data):
        if not is_safe_path(self.cache_file):
            raise PermissionError(f"Security Boundary Violation: Path {self.cache_file} is out of bounds.")
            
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)

    def load_registry(self, force_rebuild=False):
        """
        Loads the registry. If cache is valid, returns index in <20ms.
        If changes are detected, runs incremental update (ADR-005).
        """
        start_time = time.time()
        
        # 1. Scan filesystem for signatures
        current_signatures = self.scanner.scan_roots()
        
        # 2. Check cache
        cache_data = None
        if not force_rebuild:
            cache_data = self._load_cache_file()
            
        if not cache_data or "skills" not in cache_data or "signatures" not in cache_data:
            # Rebuild cache from scratch
            print("Registry cache missing or invalid. Performing full scan...")
            cache_data = {"skills": {}, "signatures": {}}
            
        cached_skills = cache_data["skills"]
        cached_signatures = cache_data["signatures"]
        
        updated_skills = {}
        changes_detected = False
        
        # 3. Incremental Validation
        # Find new or modified skills
        for skill_id, sig in current_signatures.items():
            cached_sig = cached_signatures.get(skill_id)
            
            # If modification time or size changed, or skill is new
            if not cached_sig or cached_sig["mtime"] != sig["mtime"] or cached_sig["size"] != sig["size"]:
                changes_detected = True
                print(f"Incremental refresh: parsing skill '{skill_id}'...")
                parsed = self.parser.parse_skill(sig["file_path"])
                if parsed:
                    updated_skills[skill_id] = parsed
            else:
                # Retain cached skill object
                if skill_id in cached_skills:
                    updated_skills[skill_id] = cached_skills[skill_id]
                else:
                    # Inconsistency: signature exists but skill object missing
                    changes_detected = True
                    parsed = self.parser.parse_skill(sig["file_path"])
                    if parsed:
                        updated_skills[skill_id] = parsed

        # Find deleted skills
        for skill_id in list(cached_skills.keys()):
            if skill_id not in current_signatures:
                changes_detected = True
                print(f"Incremental refresh: removing skill '{skill_id}'...")

        # 4. Save and return registry
        if changes_detected:
            cache_data["skills"] = updated_skills
            cache_data["signatures"] = current_signatures
            cache_data["last_updated"] = time.time()
            self._save_cache_file(cache_data)
            
        elapsed_ms = int((time.time() - start_time) * 1000)
        sys.stdout.write(f"Registry load completed in {elapsed_ms}ms (changes_detected={changes_detected}).\n")
        
        return cache_data["skills"]

    def find_by_capability(self, registry, capability):
        """
        Query capability index. Matches keywords, languages, and frameworks.
        """
        matches = []
        cap_lower = capability.lower()
        
        for skill_id, skill in registry.items():
            score = 0
            # Matches against name
            if cap_lower in skill["name"].lower():
                score += 30
            # Matches in languages/frameworks
            if any(cap_lower == lang.lower() for lang in skill["languages"]):
                score += 50
            if any(cap_lower == fw.lower() for fw in skill["frameworks"]):
                score += 50
            # Matches in keywords
            if any(cap_lower == kw.lower() for kw in skill["keywords"]):
                score += 20
            # Matches in description
            if cap_lower in skill["description"].lower():
                score += 10
                
            if score > 0:
                skill_copy = skill.copy()
                skill_copy["match_score"] = score
                matches.append(skill_copy)
                
        # Sort by relevance score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

if __name__ == "__main__":
    cache = RegistryCache(".")
    reg = cache.load_registry()
    if len(sys.argv) > 1:
        query = sys.argv[1]
        results = cache.find_by_capability(reg, query)
        print(f"\nQuery results for '{query}':")
        for r in results[:5]:
            print(f" - {r['id']} (Score: {r['match_score']}, Division: {r['division']})")