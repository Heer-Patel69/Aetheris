import os
import json
import sys
from pathlib import Path
from kernel.utils import is_safe_path, redact_secrets, initialize_perimeter

# Attempt to load pyyaml
try:
    import yaml
except ImportError:
    sys.stderr.write("CRITICAL: 'pyyaml' is required by Memory Engine.\n")
    sys.exit(1)

class MemoryEngine:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        initialize_perimeter(self.workspace_path)
        
        self.global_memory_dir = Path("~/.aetheris/memory").expanduser()
        self.project_memory_dir = self.workspace_path / ".aetheris/memory"
        
        # Ensure directories exist
        if is_safe_path(self.global_memory_dir):
            self.global_memory_dir.mkdir(parents=True, exist_ok=True)
        if is_safe_path(self.project_memory_dir):
            self.project_memory_dir.mkdir(parents=True, exist_ok=True)

    def _safe_read_yaml(self, file_path):
        """
        Safely read a YAML file and catch parsing corruptions.
        """
        if not file_path.exists():
            return None
            
        if not is_safe_path(file_path):
            raise PermissionError(f"Security Boundary Violation: Path {file_path} is out of bounds.")
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except (yaml.YAMLError, ValueError) as e:
            sys.stderr.write(f"Memory Corruption Warning: File {file_path} is corrupted. Resetting. Error: {e}\n")
            # Self-healing: Delete corrupted file
            try:
                file_path.unlink()
            except Exception:
                pass
            return None

    def _safe_write_yaml(self, file_path, data):
        """
        Safely write data to YAML, verifying path constraints.
        """
        if not is_safe_path(file_path):
            raise PermissionError(f"Security Boundary Violation: Path {file_path} is out of bounds.")
            
        serialized = yaml.safe_dump(data, default_flow_style=False)
        scrubbed = redact_secrets(serialized)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(scrubbed)

    def get_profile(self):
        """
        Loads the cached Project Profile. Returns None if missing/stale.
        """
        profile_path = self.project_memory_dir / "project-profile.yaml"
        return self._safe_read_yaml(profile_path)

    def save_profile(self, profile):
        """
        Saves the Project Profile to workspace memory.
        """
        profile_path = self.project_memory_dir / "project-profile.yaml"
        self._safe_write_yaml(profile_path, profile)

    def get_conventions(self):
        """
        Loads the conventions cache.
        """
        conventions_path = self.project_memory_dir / "conventions.yaml"
        data = self._safe_read_yaml(conventions_path)
        return data if data else {}

    def save_conventions(self, conventions):
        conventions_path = self.project_memory_dir / "conventions.yaml"
        self._safe_write_yaml(conventions_path, conventions)

    def get_decisions(self):
        """
        Read append-only ADR decision log (JSONL).
        """
        decisions_path = self.project_memory_dir / "decisions.jsonl"
        if not decisions_path.exists():
            return []
            
        if not is_safe_path(decisions_path):
            raise PermissionError(f"Security Boundary Violation: Path {decisions_path} is out of bounds.")
            
        decisions = []
        try:
            with open(decisions_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        decisions.append(json.loads(line.strip()))
            return decisions
        except Exception as e:
            sys.stderr.write(f"Decision Log Corruption: resetting decisions log. Error: {e}\n")
            try:
                decisions_path.unlink()
            except Exception:
                pass
            return []

    def save_decision(self, decision_record):
        """
        Append a decision record to the JSONL log.
        """
        decisions_path = self.project_memory_dir / "decisions.jsonl"
        if not is_safe_path(decisions_path):
            raise PermissionError(f"Security Boundary Violation: Path {decisions_path} is out of bounds.")
            
        line = json.dumps(decision_record)
        scrubbed_line = redact_secrets(line)
        
        with open(decisions_path, "a", encoding="utf-8") as f:
            f.write(scrubbed_line + "\n")

    def verify_fingerprint(self, current_fingerprint):
        """
        Compare active fingerprint with the cached profile fingerprint.
        """
        profile = self.get_profile()
        if not profile:
            return False
        cached_fingerprint = profile.get("fingerprint")
        return cached_fingerprint == current_fingerprint