import os
import json
import time
import hashlib
import fnmatch
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Standard Event Bus interface
try:
    from kernel.event_bus import EventBus
except ImportError:
    class EventBus:
        def __init__(self, workspace_path, telemetry=None):
            self.workspace_path = workspace_path
        def publish(self, event_type, publisher, payload, priority="NORMAL"):
            pass

class IgnoreRuleManager:
    """Manages glob-based file and directory exclusion rules, including .gitignore."""
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.default_ignores = {
            ".git", "node_modules", "dist", "build", "coverage", ".next", 
            "venv", ".venv", ".aetheris", "__pycache__", ".DS_Store", "out"
        }
        self.gitignore_rules = self._load_gitignore()

    def _load_gitignore(self) -> List[str]:
        rules = []
        gitignore_path = self.workspace_path / ".gitignore"
        if gitignore_path.exists():
            try:
                content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Normalize pattern for fnmatch matching
                        rules.append(line)
            except Exception:
                pass
        return rules

    def is_ignored(self, path: Path) -> bool:
        # Check defaults first
        try:
            rel_parts = path.relative_to(self.workspace_path).parts
            if any(part in self.default_ignores for part in rel_parts):
                return True
            
            # Check gitignore rules against relative path string
            rel_path_str = str(path.relative_to(self.workspace_path)).replace("\\", "/")
            for rule in self.gitignore_rules:
                # Handle directory-specific ignore trailing slashes
                rule_normalized = rule.rstrip("/")
                if fnmatch.fnmatch(rel_path_str, rule_normalized) or \
                   any(fnmatch.fnmatch(part, rule_normalized) for part in rel_parts):
                    return True
        except Exception:
            pass
        return False


class DirectoryWalker:
    """Recursively walks a workspace, filtering out ignored folders and files up to a depth cap."""
    def __init__(self, ignore_manager: IgnoreRuleManager):
        self.ignore_manager = ignore_manager

    def walk(self, root_path: Path, max_depth: int = 3) -> List[Path]:
        files_found = []
        root_resolved = root_path.resolve()
        
        # Iterative stack-based walk to ensure deterministic depth control
        stack: List[Tuple[Path, int]] = [(root_resolved, 0)]
        visited_dirs: Set[Path] = set()

        while stack:
            curr_dir, depth = stack.pop()
            
            if curr_dir in visited_dirs or depth > max_depth:
                continue
            visited_dirs.add(curr_dir)

            try:
                for entry in curr_dir.iterdir():
                    if self.ignore_manager.is_ignored(entry):
                        continue
                        
                    if entry.is_dir():
                        stack.append((entry, depth + 1))
                    elif entry.is_file():
                        files_found.append(entry)
            except (PermissionError, FileNotFoundError):
                # Safe fallback: skip unreadable folders
                pass
                
        return sorted(files_found)


class FileFingerprintManager:
    """Calculates file signatures and checks for modifications against cached states."""
    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        try:
            # For performance, hash small file segments or metadata hashes for large files
            stat = file_path.stat()
            meta_string = f"{file_path.name}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.sha256(meta_string.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    @classmethod
    def analyze_deltas(cls, current_files: List[Path], cached_fingerprints: Dict[str, str]) -> Tuple[List[Path], List[str]]:
        modified_or_new = []
        deleted = []
        
        current_rel_paths = set()
        for fpath in current_files:
            try:
                rel_path = fpath.name # Simple mapping or relative to root
                # Find real relative path
                current_rel_paths.add(str(fpath))
            except Exception:
                pass
                
        # Deleted check
        for cached_path in cached_fingerprints:
            if cached_path not in current_rel_paths:
                deleted.append(cached_path)
                
        # Modified/new check
        for fpath in current_files:
            fpath_str = str(fpath)
            curr_hash = cls.calculate_sha256(fpath)
            if cached_fingerprints.get(fpath_str) != curr_hash:
                modified_or_new.append(fpath)
                
        return modified_or_new, deleted


class DiscoveryCache:
    """Reads and writes fingerprint database cache files."""
    def __init__(self, workspace_path: Path):
        self.cache_file = workspace_path / ".aetheris" / "cache" / "fingerprints.json"

    def load(self) -> Dict[str, str]:
        if not self.cache_file.exists():
            return {}
        try:
            return json.loads(self.cache_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, data: Dict[str, str]) -> None:
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass


class LanguageDetector:
    """Identifies programming languages based on file extensions and content shebangs."""
    SUFFIX_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".md": "markdown",
        ".prisma": "prisma",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".sh": "shell",
        ".ps1": "powershell",
        ".dockerfile": "dockerfile"
    }

    def detect(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in self.SUFFIX_MAP:
            return self.SUFFIX_MAP[suffix]
        
        if file_path.name.lower() == "dockerfile":
            return "dockerfile"
            
        # Inspect shebang for extensionless scripts
        try:
            if file_path.stat().st_size < 1024:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    first_line = f.readline()
                    if first_line.startswith("#!"):
                        if "python" in first_line:
                            return "python"
                        if "node" in first_line:
                            return "javascript"
                        if "sh" in first_line or "bash" in first_line:
                            return "shell"
        except Exception:
            pass
            
        return "unknown"


class FrameworkDetector:
    """Detects installed libraries, tools, and structures with confidence ratings."""
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path

    def detect(self, dependencies: Dict[str, str], files: List[Path]) -> Dict[str, Dict[str, any]]:
        frameworks = {}
        file_names = {f.name.lower() for f in files}

        # 1. Next.js
        if "next" in dependencies or "next.config.js" in file_names or "next.config.mjs" in file_names:
            frameworks["nextjs"] = {
                "confidence": 0.98,
                "evidence": "next dependency or configuration file detected"
            }
            
        # 2. React
        if "react" in dependencies:
            frameworks["react"] = {
                "confidence": 0.95,
                "evidence": "react dependency detected in package manifest"
            }

        # 3. Tailwind CSS
        if "tailwindcss" in dependencies or "tailwind.config.js" in file_names or "tailwind.config.ts" in file_names:
            frameworks["tailwind"] = {
                "confidence": 0.98,
                "evidence": "tailwindcss package or config file detected"
            }

        # 4. Prisma ORM
        if "prisma" in dependencies or any(f.suffix == ".prisma" for f in files):
            frameworks["prisma"] = {
                "confidence": 0.95,
                "evidence": "prisma schemas or dependencies detected"
            }

        # 5. Docker containerization
        if "dockerfile" in file_names or "docker-compose.yml" in file_names or "docker-compose.yaml" in file_names:
            frameworks["docker"] = {
                "confidence": 0.99,
                "evidence": "Dockerfile or Docker Compose file discovered in workspace"
            }
            
        # 6. SQLite
        if any("sqlite" in f.name.lower() or f.suffix == ".db" for f in files):
            frameworks["sqlite"] = {
                "confidence": 0.85,
                "evidence": "local .db database or sqlite file signatures detected"
            }

        return frameworks


class DependencyDetector:
    """Extracts package dependencies and requirements from package managers."""
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path

    def extract(self, files: List[Path]) -> Tuple[str, Dict[str, str]]:
        package_manager = "none"
        dependencies = {}

        file_names = {f.name.lower() for f in files}

        # 1. Node.js (package.json)
        if "package.json" in file_names:
            package_manager = "npm"
            # Look for lockfiles to refine manager
            if "yarn.lock" in file_names:
                package_manager = "yarn"
            elif "pnpm-lock.yaml" in file_names:
                package_manager = "pnpm"
                
            pkg_file = next((f for f in files if f.name.lower() == "package.json"), None)
            if pkg_file:
                try:
                    data = json.loads(pkg_file.read_text(encoding="utf-8", errors="ignore"))
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    dependencies.update(deps)
                    dependencies.update(dev_deps)
                except Exception:
                    pass

        # 2. Python (requirements.txt / pipfile / pyproject.toml)
        elif "requirements.txt" in file_names:
            package_manager = "pip"
            req_file = next((f for f in files if f.name.lower() == "requirements.txt"), None)
            if req_file:
                try:
                    for line in req_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = line.split("==")
                            if len(parts) == 2:
                                dependencies[parts[0].strip()] = parts[1].strip()
                            else:
                                dependencies[line] = "latest"
                except Exception:
                    pass
        
        elif "pyproject.toml" in file_names:
            package_manager = "pip"
            # Simple fallback parser for pyproject toml
            toml_file = next((f for f in files if f.name.lower() == "pyproject.toml"), None)
            if toml_file:
                try:
                    content = toml_file.read_text(encoding="utf-8", errors="ignore")
                    # Crude extraction of dependencies block
                    matches = re.findall(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
                    if matches:
                        for match in matches[0].split(','):
                            dep = match.strip().strip('"').strip("'")
                            if dep:
                                dependencies[dep] = "latest"
                except Exception:
                    pass

        return package_manager, dependencies


class GitMetadataCollector:
    """Retrieves local git branch, commit hash, and status flag."""
    def collect(self, workspace_path: Path) -> Dict[str, any]:
        metadata = {
            "git_branch": "none",
            "git_commit": "none",
            "git_dirty": False
        }
        
        git_dir = workspace_path / ".git"
        if not git_dir.exists():
            return metadata

        try:
            # Fetch branch name
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(workspace_path),
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            metadata["git_branch"] = branch
            
            # Fetch commit hash
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=str(workspace_path),
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            metadata["git_commit"] = commit
            
            # Fetch dirty state
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=str(workspace_path),
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            metadata["git_dirty"] = len(status) > 0
        except Exception:
            # Git CLI might be missing, fall back to safe parsing files directly
            try:
                head_file = git_dir / "HEAD"
                if head_file.exists():
                    ref = head_file.read_text(encoding="utf-8").strip()
                    if ref.startswith("ref:"):
                        branch_name = ref.split("refs/heads/")[-1]
                        metadata["git_branch"] = branch_name
                        ref_file = git_dir / "refs" / "heads" / branch_name
                        if ref_file.exists():
                            metadata["git_commit"] = ref_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass
                
        return metadata


class SchemaValidator:
    """Validates the structure and data types of WDE and URUE JSON outputs."""
    @staticmethod
    def validate_wde_schemas(inventories: Dict[str, dict]) -> bool:
        # Schema 1: workspace.inventory
        inv = inventories.get("workspace.inventory")
        if not inv or "workspace_root" not in inv or "files" not in inv:
            return False
        for f in inv["files"]:
            if not all(k in f for k in ("path", "size_bytes", "modified_at", "fingerprint")):
                return False

        # Schema 2: filesystem.graph
        graph = inventories.get("filesystem.graph")
        if not graph or "nodes" not in graph or "edges" not in graph:
            return False

        # Schema 3: workspace.metadata
        meta = inventories.get("workspace.metadata")
        if not meta or not all(k in meta for k in ("total_files", "total_directories", "git_branch", "git_commit")):
            return False

        # Schema 4: language.inventory
        lang = inventories.get("language.inventory")
        if not lang or "languages" not in lang:
            return False

        # Schema 5: framework.inventory
        fw = inventories.get("framework.inventory")
        if not fw or "frameworks" not in fw:
            return False

        # Schema 6: dependency.inventory
        dep = inventories.get("dependency.inventory")
        if not dep or "package_manager" not in dep or "dependencies" not in dep:
            return False

        return True


class WorkspaceDiscoveryEngine:
    """Coordinator orchestration engine executing the WDE pipeline."""
    def __init__(self, workspace_path: str, event_bus: EventBus = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.event_bus = event_bus if event_bus else EventBus(self.workspace_path)
        self.cache = DiscoveryCache(self.workspace_path)
        self.output_dir = self.workspace_path / ".aetheris" / "execution"
        
        # Sub-components registration
        self.ignore_manager = IgnoreRuleManager(self.workspace_path)
        self.walker = DirectoryWalker(self.ignore_manager)
        self.lang_detector = LanguageDetector()
        self.framework_detector = FrameworkDetector(self.workspace_path)
        self.dependency_detector = DependencyDetector(self.workspace_path)
        self.git_collector = GitMetadataCollector()

    def scan(self) -> Dict[str, dict]:
        """Main execution runner compiling the 6 inventory models."""
        self.event_bus.publish("WorkspaceDiscoveryStarted", "WDE", {"workspace": str(self.workspace_path)})
        start_time = time.time()
        
        # 1. Walk Directories
        all_files = self.walker.walk(self.workspace_path)
        
        # 2. Delta modification checking using Cache
        cached_fingerprints = self.cache.load()
        modified_or_new, deleted = FileFingerprintManager.analyze_deltas(all_files, cached_fingerprints)
        
        # Rebuild fingerprint database
        current_fingerprints = {}
        for fpath in all_files:
            fpath_str = str(fpath)
            current_fingerprints[fpath_str] = FileFingerprintManager.calculate_sha256(fpath)
        self.cache.save(current_fingerprints)

        # 3. File Inventory compilation
        files_list = []
        for fpath in all_files:
            try:
                stat = fpath.stat()
                files_list.append({
                    "path": str(fpath.relative_to(self.workspace_path)).replace("\\", "/"),
                    "size_bytes": stat.st_size,
                    "modified_at": stat.st_mtime,
                    "fingerprint": current_fingerprints.get(str(fpath), ""),
                    "mime_type": "text/plain" # Simple default
                })
            except Exception:
                pass
                
        workspace_inventory = {
            "workspace_root": str(self.workspace_path).replace("\\", "/"),
            "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "files": files_list
        }

        # 4. Filesystem Graph compilation
        nodes = []
        edges = []
        for f in files_list:
            nodes.append({"id": f"file:{f['path']}", "type": "File"})
            
        # Detect imports to construct edges (simple extraction regex for graph verification)
        for fpath in all_files:
            rel_path = str(fpath.relative_to(self.workspace_path)).replace("\\", "/")
            if fpath.suffix == ".py":
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    for m in re.findall(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", content, re.MULTILINE):
                        edges.append({
                            "source": f"file:{rel_path}",
                            "target": f"import:{m}",
                            "relationship": "depends_on"
                        })
                except Exception:
                    pass
                    
        filesystem_graph = {
            "nodes": nodes,
            "edges": edges
        }

        # 5. Git & General Metadata
        git_info = self.git_collector.collect(self.workspace_path)
        workspace_metadata = {
            "total_files": len(all_files),
            "total_directories": len({f.parent for f in all_files}),
            "git_branch": git_info["git_branch"],
            "git_commit": git_info["git_commit"],
            "git_dirty": git_info["git_dirty"]
        }

        # 6. Languages Inventory
        lang_counts = {}
        for fpath in all_files:
            lang = self.lang_detector.detect(fpath)
            if lang != "unknown":
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
                
        total_lang_files = sum(lang_counts.values()) or 1
        languages_inventory = {
            "languages": {
                k: {
                    "file_count": v,
                    "percentage": round(v / total_lang_files, 2)
                } for k, v in lang_counts.items()
            }
        }

        # 7. Dependencies & Frameworks
        pkg_manager, dependencies = self.dependency_detector.extract(all_files)
        dependency_inventory = {
            "package_manager": pkg_manager,
            "dependencies": dependencies
        }
        
        frameworks = self.framework_detector.detect(dependencies, all_files)
        framework_inventory = {
            "frameworks": frameworks
        }

        # Pack inventories
        inventories = {
            "workspace.inventory": workspace_inventory,
            "filesystem.graph": filesystem_graph,
            "workspace.metadata": workspace_metadata,
            "language.inventory": languages_inventory,
            "framework.inventory": framework_inventory,
            "dependency.inventory": dependency_inventory
        }

        # 8. Schema Validation & Write files
        valid = SchemaValidator.validate_wde_schemas(inventories)
        if not valid:
            raise ValueError("WDE JSON output fails strict schema validation.")
            
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in inventories.items():
            out_file = self.output_dir / f"{name}.json"
            out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

        elapsed_ms = int((time.time() - start_time) * 1000)
        self.event_bus.publish("WorkspaceDiscoveryCompleted", "WDE", {
            "elapsed_ms": elapsed_ms,
            "files_count": len(all_files)
        })

        return inventories

import re
