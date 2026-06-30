import os
import json
import time
from pathlib import Path
from kernel.recovery import AutonomousRecoveryEngine

class RuntimeScheduler:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.state_file_path = self.workspace_path / ".aetheris" / "execution_state.json"
        
    def _save_state(self, milestone, tasks):
        """
        Saves current execution checkpoints.
        """
        try:
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            state_data = {
                "session_id": "sess-autonomous",
                "current_milestone": milestone,
                "tasks": tasks
            }
            self.state_file_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def execute_dag(self, dag_tasks):
        """
        Loops over each task in the DAG sequentially, simulating execution
        and invoking the AutonomousRecoveryEngine on errors.
        """
        tasks_state = [{"task_id": f"t-{i}", "name": t, "status": "Pending"} for i, t in enumerate(dag_tasks)]
        
        for i, task_name in enumerate(dag_tasks):
            print(f"Executing task: {task_name}...")
            tasks_state[i]["status"] = "Running"
            self._save_state(task_name, tasks_state)
            
            # Simulate a build failure and recovery during "unit_testing" to test Self-Healing
            if task_name == "unit_testing":
                print("[ERROR] Build failed: SyntaxError in tests/test_auth.py: Line 12 - missing close parenthesis.")
                tasks_state[i]["status"] = "Failed"
                self._save_state(task_name, tasks_state)
                
                # Trigger Autonomous Recovery Engine
                recovery = AutonomousRecoveryEngine(self.workspace_path)
                rca = recovery.perform_rca("SyntaxError: unmatched ')' in test_auth.py line 12")
                fixed = recovery.apply_remediation(rca)
                
                if fixed:
                    tasks_state[i]["status"] = "Completed"
                    self._save_state(task_name, tasks_state)
                    print(f"Task {task_name} successfully recovered and completed.")
                else:
                    print(f"Task {task_name} failed recovery.")
            else:
                # Normal successful execution
                time.sleep(0.1)
                tasks_state[i]["status"] = "Completed"
                self._save_state(task_name, tasks_state)
                print(f"Task {task_name} completed.")
                
        return True
