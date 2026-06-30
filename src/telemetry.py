import os
import json
import time
from pathlib import Path
from utils import is_safe_path

class TelemetryEngine:
    def __init__(self, workspace_path, log_dir=None, max_size_mb=200):
        self.workspace_path = Path(workspace_path).resolve()
        
        if log_dir:
            self.global_log_dir = Path(log_dir).resolve()
        else:
            self.global_log_dir = Path("~/.univoid/brain/logs").expanduser()
            
        self.project_log_dir = self.workspace_path / ".univoid/telemetry"
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Ensure log directories exist safely
        if is_safe_path(self.global_log_dir):
            self.global_log_dir.mkdir(parents=True, exist_ok=True)
        if is_safe_path(self.project_log_dir):
            self.project_log_dir.mkdir(parents=True, exist_ok=True)

    def _mask_paths(self, obj):
        """
        Recursively mask sensitive system paths and usernames.
        """
        username = os.environ.get("USERNAME", os.environ.get("USER", ""))
        user_home = str(Path("~").expanduser().resolve())
        
        if isinstance(obj, str):
            masked = obj
            if username:
                # Mask username in standard path formats
                masked = masked.replace(username, "<user>")
                masked = masked.replace(username.lower(), "<user>")
            # Mask complete home paths
            masked = masked.replace(user_home, "~")
            return masked
            
        elif isinstance(obj, dict):
            return {key: self._mask_paths(val) for key, val in obj.items()}
            
        elif isinstance(obj, list):
            return [self._mask_paths(item) for item in obj]
            
        return obj

    def _rotate_logs(self, log_file):
        """
        Rotate logs if the trace file exceeds the size budget (ADR-002).
        """
        if not log_file.exists():
            return
            
        if log_file.stat().st_size > self.max_size_bytes:
            backup = log_file.with_name(f"{log_file.name}.1")
            if backup.exists():
                backup.unlink() # Delete oldest log
            log_file.rename(backup)

    def _write_log(self, data):
        """
        Stateless append of event records to the JSONL log (ADR-007).
        """
        masked_data = self._mask_paths(data)
        
        # Write to global log path
        global_log_file = self.global_log_dir / "execution-trace.jsonl"
        if is_safe_path(global_log_file):
            try:
                self._rotate_logs(global_log_file)
                with open(global_log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(masked_data) + "\n")
            except Exception as e:
                # Fallback print to stderr on write locks/I/O limits
                import sys
                sys.stderr.write(f"Telemetry Write Failure (Global): {e}\n")
                
        # Write to local project-specific log path
        project_log_file = self.project_log_dir / "pipeline-runs.jsonl"
        if is_safe_path(project_log_file):
            try:
                self._rotate_logs(project_log_file)
                with open(project_log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(masked_data) + "\n")
            except Exception as e:
                import sys
                sys.stderr.write(f"Telemetry Write Failure (Project): {e}\n")

    def log_stage_start(self, session_id, stage):
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": session_id,
            "event": "StageStarted",
            "stage": stage
        }
        self._write_log(record)

    def log_stage_complete(self, session_id, stage, duration_ms, metadata=None):
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": session_id,
            "event": "StageCompleted",
            "stage": stage,
            "duration_ms": duration_ms,
            "metadata": metadata if metadata else {}
        }
        self._write_log(record)

    def log_stage_failed(self, session_id, stage, error, duration_ms):
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": session_id,
            "event": "StageFailed",
            "stage": stage,
            "duration_ms": duration_ms,
            "error": str(error)
        }
        self._write_log(record)
