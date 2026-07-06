import os
import json
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from kernel.providers.base import ExecutionCapability

class ECCProvider(ExecutionCapability):
    """
    Concrete capability provider mapping the 'hooks' and 'agents' capability to Everything Claude Code (ECC).
    Runs Claude Code CLI as an isolated subprocess, injecting context extracted from engineering manifest.
    """

    def __init__(self, workspace_path: str):
        self.workspace_root = Path(workspace_path).resolve()
        self.manifest_path = self.workspace_root / ".aetheris" / "state" / "ENGINEERING_MANIFEST.json"
        self._status = "stopped"

    def initialize(self, config: Dict[str, Any]) -> None:
        self.manifest_path = self.workspace_root / ".aetheris" / "state" / "ENGINEERING_MANIFEST.json"

    def start(self) -> bool:
        self._status = "running"
        return True

    def stop(self) -> bool:
        self._status = "stopped"
        return True

    def get_status(self) -> str:
        return self._status

    def _load_manifest(self) -> Dict[str, Any]:
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception as e:
                import sys
                sys.stderr.write(f"Warning: Failed to load manifest {self.manifest_path}: {e}\n")
        return {
            "current_phase": "Phase 2: Ingestion & Skill Translation",
            "task_id": "sys-integration",
            "rules": []
        }

    def prepare_environment(self) -> Dict[str, str]:
        manifest = self._load_manifest()
        env = os.environ.copy()
        
        env["AETHERIS_ACTIVE_PHASE"] = str(manifest.get("current_phase", "unknown"))
        env["AETHERIS_TASK_ID"] = str(manifest.get("task_id", "unknown"))
        env["AETHERIS_MANIFEST_DATA"] = json.dumps(manifest)
        env["CLAUDE_CODE_STATELESS"] = "1"
        
        return env

    def execute(self, args: List[str], stdin_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the Claude Code subprocess synchronously, capturing output.
        """
        env = self.prepare_environment()
        cmd = ["claude"] + args
        if os.name == "nt":
            executable = shutil.which("claude")
            if not executable:
                cmd = ["npx.cmd", "@anthropic-ai/claude-code"] + args
        else:
            executable = shutil.which("claude")
            if not executable:
                cmd = ["npx", "@anthropic-ai/claude-code"] + args

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if stdin_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.workspace_root),
                env=env,
                shell=True if os.name == "nt" else False
            )
            stdout, stderr = proc.communicate(
                input=stdin_data.encode("utf-8") if stdin_data else None
            )
            return {
                "exit_code": proc.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "success": proc.returncode == 0
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Process execution failed: {e}",
                "success": False
            }
