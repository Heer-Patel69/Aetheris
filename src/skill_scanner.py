import os
import sys
from pathlib import Path
from utils import is_safe_path

class SkillScanner:
    def __init__(self, roots=None):
        """
        Initialize scanner with list of search roots.
        """
        if roots:
            self.roots = [Path(r).resolve() for r in roots]
        else:
            self.roots = [
                Path("~/.gemini/config/skills").expanduser().resolve()
            ]
            
    def add_root(self, root_path):
        resolved = Path(root_path).resolve()
        if resolved not in self.roots:
            self.roots.append(resolved)

    def scan_roots(self):
        """
        Traverse all roots and locate folders containing 'SKILL.md' files.
        Collects file modification times and sizes to check for changes (ADR-005).
        """
        discovered_skills = {}
        
        for root in self.roots:
            if not root.exists():
                continue
                
            if not is_safe_path(root):
                # Skip out-of-bounds roots silently to protect security perimeter
                continue
                
            try:
                # Traverse subfolders at depth 1 (every skill is a subdirectory in the root)
                for entry in os.scandir(root):
                    if entry.is_dir():
                        try:
                            # Direct stat call to reduce filesystem lookups on Windows (ADR-005)
                            skill_file_path = os.path.join(entry.path, "SKILL.md")
                            stat = os.stat(skill_file_path)
                            discovered_skills[entry.name] = {
                                "skill_id": entry.name,
                                "dir_path": entry.path,
                                "file_path": skill_file_path,
                                "size": stat.st_size,
                                "mtime": stat.st_mtime
                            }
                        except FileNotFoundError:
                            continue
            except Exception as e:
                sys.stderr.write(f"SkillScanner warning: directory scan failed on {root}: {e}\n")

                
        return discovered_skills

if __name__ == "__main__":
    scanner = SkillScanner()
    skills = scanner.scan_roots()
    import json
    print(json.dumps(skills, indent=2))
