import os
import sys
import json
import hashlib
from pathlib import Path
from kernel.utils import is_safe_path, redact_secrets, initialize_perimeter

# Critical configuration folders to look for
STACK_INDICATORS = {
    "package.json": "javascript/typescript",
    "tsconfig.json": "typescript",
    "composer.json": "php",
    "requirements.txt": "python",
    "Pipfile": "python",
    "pyproject.toml": "python",
    "Gemfile": "ruby",
    "cargo.toml": "rust",
    "go.mod": "go",
    "docker-compose.yml": "docker",
    "Dockerfile": "docker",
    "supabase/config.toml": "supabase",
    "firebase.json": "firebase",
    "next.config.js": "nextjs",
    "next.config.mjs": "nextjs",
    "vite.config.ts": "vite",
    "vite.config.js": "vite",
    "tailwind.config.js": "tailwind",
    "tailwind.config.ts": "tailwind"
}

IGNORED_DIRS = {".git", "node_modules", "dist", "build", "coverage", ".next", "venv", ".venv"}

class ProjectScanner:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        initialize_perimeter(self.workspace_path)
        
    def _calculate_fingerprint(self, found_files):
        """
        Generates a SHA-256 hash representing the state of key project files (ADR-005).
        """
        hasher = hashlib.sha256()
        # Sort files to ensure deterministic hash ordering
        for path in sorted(found_files):
            try:
                # Add path name, size, and modification time
                stat = path.stat()
                file_metadata = f"{path.relative_to(self.workspace_path)}:{stat.st_size}:{stat.st_mtime}"
                hasher.update(file_metadata.encode("utf-8"))
            except Exception:
                pass
        return hasher.hexdigest()

    def _parse_package_json(self, file_path, profile):
        """
        Parse package.json dependencies and populate profile (conventions/frameworks).
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            
            # Framework/conv detection from dependencies
            if "react" in all_deps:
                profile["frameworks"]["react"] = {"confidence": 0.98, "evidence": "react dependency"}
            if "next" in all_deps:
                profile["frameworks"]["nextjs"] = {"confidence": 0.98, "evidence": "next dependency"}
            if "typescript" in all_deps:
                profile["languages"]["typescript"] = {"confidence": 0.98, "evidence": "typescript dependency"}
            if "tailwindcss" in all_deps:
                profile["conventions"]["styling"] = "tailwind"
            if "vitest" in all_deps or "jest" in all_deps:
                profile["conventions"]["testing"] = "jest/vitest"
                
            profile["package_manager"] = "npm" # Default fallback
            # Look for lockfiles to determine package manager
            if (self.workspace_path / "yarn.lock").exists():
                profile["package_manager"] = "yarn"
            elif (self.workspace_path / "pnpm-lock.yaml").exists():
                profile["package_manager"] = "pnpm"
            elif (self.workspace_path / "package-lock.json").exists():
                profile["package_manager"] = "npm"
                
        except Exception as e:
            sys.stderr.write(f"Error parsing package.json: {e}\n")

    def scan(self):
        """
        Traverses directory tree up to depth 2, detecting indicators (ADR-001).
        """
        if not is_safe_path(self.workspace_path):
            raise PermissionError(f"Security Boundary Violation: Access denied to path {self.workspace_path}")
            
        profile = {
            "schema_version": "2.1.0",
            "workspace_root": str(self.workspace_path),
            "languages": {},
            "frameworks": {},
            "infrastructure": {},
            "conventions": {
                "file_naming": "unknown",
                "styling": "unknown",
                "testing": "unknown"
            },
            "monorepo": False,
            "package_manager": "unknown",
            "fingerprint": ""
        }
        
        found_indicators = []
        
        # Traverse root and depth 1 subdirectories
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                # Calculate current depth relative to root
                rel_path = Path(root).relative_to(self.workspace_path)
                depth = len(rel_path.parts)
                
                # Enforce traversal depth ceiling (max depth = 2, i.e., root and immediate subfolders)
                if depth >= 2:
                    dirs.clear() # Stop recursion deeper
                    continue
                    
                # Prune ignored folders in-place
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
                
                # Check for indicators in the current folder files
                for f in files:
                    file_path = Path(root) / f
                    if f in STACK_INDICATORS:
                        found_indicators.append(file_path)
                        # Add raw indicators mapping
                        lang_fam = STACK_INDICATORS[f]
                        if "/" in lang_fam:
                            pass
                        elif lang_fam == "typescript" or lang_fam == "python":
                            profile["languages"][lang_fam] = {"confidence": 0.90, "evidence": f"{f} exists"}
                        elif lang_fam == "supabase" or lang_fam == "firebase":
                            profile["infrastructure"][lang_fam] = {"type": lang_fam, "evidence": f"{f} exists"}
                            
            # Process package.json if found
            pkg_json = self.workspace_path / "package.json"
            if pkg_json.exists():
                self._parse_package_json(pkg_json, profile)
                
            # Fingerprint indicator list
            profile["fingerprint"] = self._calculate_fingerprint(found_indicators)
            
            # Simple convention naming check: scan file names in root
            root_files = [f for f in os.listdir(self.workspace_path) if os.path.isfile(self.workspace_path / f)]
            if root_files:
                kebab_count = sum(1 for f in root_files if "-" in f)
                camel_count = sum(1 for f in root_files if any(c.isupper() for c in f) and "_" not in f and "-" not in f)
                if kebab_count > camel_count:
                    profile["conventions"]["file_naming"] = "kebab-case"
                elif camel_count > kebab_count:
                    profile["conventions"]["file_naming"] = "CamelCase"
                    
            return profile
            
        except Exception as e:
            sys.stderr.write(f"Scanner sweep error: {e}\n")
            profile["fingerprint"] = hashlib.sha256(b"failed").hexdigest()
            return profile

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "--workspace":
        sys.stderr.write("Usage: python scanner.py --workspace <path> --output json\n")
        sys.exit(1)
        
    ws_path = sys.argv[2]
    scanner = ProjectScanner(ws_path)
    result = scanner.scan()
    print(json.dumps(result, indent=2))