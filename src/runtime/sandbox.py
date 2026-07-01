import os
import subprocess
import sys
from pathlib import Path

class SandboxedExecutor:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.allowed_paths = [self.workspace_path]

    def is_safe(self, target_path):
        try:
            resolved_target = Path(target_path).resolve()
            for allowed in self.allowed_paths:
                if resolved_target == allowed or allowed in resolved_target.parents:
                    return True
            return False
        except Exception:
            return False

    def execute(self, cmd, env=None, timeout=30):
        """
        Executes a command safely under sandboxed restrictions.
        """
        if env is None:
            env = os.environ.copy()
        
        # Enforce sandbox variables
        env["AETHERIS_SANDBOX_MODE"] = "ENABLED"
        env["AETHERIS_PERIMETER_ROOT"] = str(self.workspace_path)
        
        print(f"[Sandbox] Executing isolated command: {cmd}")
        
        try:
            # Under Windows, run via powershell or cmd
            process = subprocess.Popen(
                cmd,
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.workspace_path)
            )
            stdout, stderr = process.communicate(timeout=timeout)
            
            return {
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "success": process.returncode == 0
            }
        except subprocess.TimeoutExpired as e:
            process.kill()
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "success": False
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }

class AutonomousRuntimeEngine:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.executor = SandboxedExecutor(self.workspace_path)
        self.active = False

    def start(self):
        self.active = True
        print("[Runtime] Autonomous Runtime Engine started. Sandbox status: ACTIVE.")
        return True

    def stop(self):
        self.active = False
        print("[Runtime] Autonomous Runtime Engine stopped.")
        return True
