import os
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import pathspec


class DiscoveryEngine:
    """Dynamic workspace scanner that crawls file trees using .gitignore-aware filtering."""

    def __init__(self, workspace_path: str = "."):
        self.root = Path(workspace_path).resolve()

    def _load_ignore_spec(self) -> pathspec.PathSpec:
        """Loads default ignore patterns alongside local .gitignore files."""
        default_patterns = [
            ".git/", "node_modules/", "venv/", ".venv/", "__pycache__/",
            "build/", "dist/", "*.egg-info/", ".aetheris/cache/"
        ]
        gitignore = self.root / ".gitignore"
        if gitignore.exists():
            with open(gitignore, "r", encoding="utf-8") as f:
                default_patterns.extend(f.readlines())
        return pathspec.PathSpec.from_lines('gitwildmatch', default_patterns)

    def dynamic_scan(self, progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """Scans workspace dynamically, classifying artifacts by structural path conventions."""
        # Programmatically sync third-party templates before scanning
        try:
            from aetheris.adapters.template_adapter import TemplateAdapter
            TemplateAdapter(str(self.root)).sync()
        except Exception as e:
            import sys
            sys.stderr.write(f"Warning: TemplateAdapter sync failed: {e}\n")

        ignore_spec = self._load_ignore_spec()
        manifest: Dict[str, list] = {"skills": [], "rfcs": [], "specs": [], "source_files": []}

        for current_root, dirs, files in os.walk(self.root):
            relative_root = Path(current_root).relative_to(self.root)

            # Prune directory tree inline to save traversal operations
            dirs[:] = [d for d in dirs if not ignore_spec.match_file(str(relative_root / d) + "/")]

            for file in files:
                file_path = Path(current_root) / file
                relative_path = file_path.relative_to(self.root)
                path_str = str(relative_path)

                if ignore_spec.match_file(path_str):
                    continue

                # Normalize to forward slashes for cross-platform path matching
                path_lower = path_str.replace("\\", "/").lower()

                # Context-aware path categorization rules
                # Filename-prefix checks take priority over directory-based rules
                # so that SPEC-*.md files inside rfcs/ are correctly classified
                file_lower = file.lower()
                if file_lower.startswith("spec-") and file.endswith(".md"):
                    manifest["specs"].append(path_str)
                elif file_lower.startswith("rfc-") and file.endswith(".md"):
                    manifest["rfcs"].append(path_str)
                elif "skills/" in path_lower and file.endswith(".md"):
                    manifest["skills"].append(path_str)
                elif "rfcs/" in path_lower and file.endswith(".md"):
                    manifest["rfcs"].append(path_str)
                elif "specs/" in path_lower and file.endswith(".md"):
                    manifest["specs"].append(path_str)
                elif file.endswith(('.py', '.js', '.ts', '.tsx', '.go', '.rs', '.java', '.cpp', '.h', '.cs')):
                    manifest["source_files"].append(path_str)

                if progress_callback:
                    progress_callback(path_str)

        return {
            "counts": {
                "skills": len(manifest["skills"]),
                "rfcs": len(manifest["rfcs"]),
                "specs": len(manifest["specs"]),
                "source_files": len(manifest["source_files"])
            },
            "artifacts": manifest
        }
