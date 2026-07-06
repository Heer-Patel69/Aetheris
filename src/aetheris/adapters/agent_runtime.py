import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

class AgentRuntimeOrchestrator:
    """
    Manages the execution of the Claude Code CLI as an isolated, stateless subprocess.
    Injects configuration context extracted from `.aetheris/ENGINEERING_MANIFEST.json`.
    """

    def __init__(self, workspace_path: str):
        self.workspace_root = Path(workspace_path).resolve()
        self.manifest_path = self.workspace_root / ".aetheris" / "ENGINEERING_MANIFEST.json"

    def _load_manifest(self) -> Dict[str, Any]:
        """Loads engineering metadata from the manifest file, falling back to safe defaults."""
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
        """
        Ingests active engineering metadata and builds environment variables
        to act as stateless context boundaries for the sub-agent.
        """
        manifest = self._load_manifest()
        env = os.environ.copy()
        
        # Inject Aetheris state controls into sub-agent environment
        env["AETHERIS_ACTIVE_PHASE"] = str(manifest.get("current_phase", "unknown"))
        env["AETHERIS_TASK_ID"] = str(manifest.get("task_id", "unknown"))
        env["AETHERIS_MANIFEST_DATA"] = json.dumps(manifest)
        
        # Invalidate local model session defaults to force clean execution loops
        env["CLAUDE_CODE_STATELESS"] = "1"
        
        return env

    async def execute_async(self, args: List[str], stdin_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the Claude Code CLI process asynchronously, returns stdout, stderr,
        and exit code.
        """
        env = self.prepare_environment()
        
        # Determine command binary (checking for 'claude' command or local npm binary)
        # Fall back to 'npx @anthropic-ai/claude-code' if 'claude' command is not global
        cmd = ["claude"] + args
        if os.name == "nt":
            # On Windows, subprocess often needs shell=True or finding the cmd file
            # Let's try running 'claude' directly, but fall back to 'npx' if needed
            executable = shutil.which("claude")
            if not executable:
                cmd = ["npx.cmd", "@anthropic-ai/claude-code"] + args
        else:
            executable = shutil.which("claude")
            if not executable:
                cmd = ["npx", "@anthropic-ai/claude-code"] + args

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE if stdin_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_root),
                env=env
            )

            stdout, stderr = await process.communicate(
                input=stdin_data.encode("utf-8") if stdin_data else None
            )

            return {
                "exit_code": process.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "success": process.returncode == 0
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Subprocess start failed: {e}",
                "success": False
            }

    def execute_sync(self, args: List[str], stdin_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Synchronous wrapper around execution for synchronous kernel steps.
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

import shutil
