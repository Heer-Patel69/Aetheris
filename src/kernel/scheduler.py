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
        Saves current execution checkpoints in both compatibility and EPE paths.
        """
        try:
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            state_data = {
                "session_id": "sess-autonomous",
                "current_milestone": milestone,
                "status": "RUNNING" if any(t["status"] in ("Running", "Pending") for t in tasks) else "COMPLETED",
                "tasks": tasks
            }
            
            # Write compatibility copy
            self.state_file_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            
            # Write EEJ state files
            exec_dir = self.workspace_path / ".aetheris" / "execution"
            exec_dir.mkdir(parents=True, exist_ok=True)
            (exec_dir / "execution_state.json").write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            
            todo = [t["name"] for t in tasks if t["status"] in ("Pending", "Failed")]
            completed = [t["name"] for t in tasks if t["status"] == "Completed"]
            
            (exec_dir / "todo.json").write_text(json.dumps(todo, indent=2), encoding="utf-8")
            (exec_dir / "completed.json").write_text(json.dumps(completed, indent=2), encoding="utf-8")
            
            # Update matching Phase Checkpoint MD file
            phases_dir = exec_dir / "phases"
            for idx, t in enumerate(tasks):
                # P0 is Requirement Analysis, tasks are P1 onwards
                checkpoint_file = phases_dir / f"P{idx}.md"
                if checkpoint_file.exists():
                    content = checkpoint_file.read_text(encoding="utf-8")
                    # Replace status in the file
                    new_status = t["status"].upper()
                    content = content.replace("Status: PENDING", f"Status: {new_status}")
                    content = content.replace("Status: RUNNING", f"Status: {new_status}")
                    checkpoint_file.write_text(content, encoding="utf-8")
                    
        except Exception:
            pass

    def execute_dag(self, dag_tasks):
        """
        Loops over each task in the DAG sequentially, simulating execution
        and invoking the AutonomousRecoveryEngine on errors.
        """
        # All milestones = Requirement Analysis + dag_tasks
        all_milestones = ["Requirement Analysis"] + dag_tasks
        tasks_state = [{"task_id": f"P{i}", "name": m, "status": "Pending"} for i, m in enumerate(all_milestones)]
        tasks_state[0]["status"] = "Completed" # Requirement Analysis is already done
        
        self._save_state(dag_tasks[0] if dag_tasks else "Requirement Analysis", tasks_state)
        
        for i, task_name in enumerate(dag_tasks):
            # Index is i+1 because P0 is Requirement Analysis
            task_idx = i + 1
            print(f"Executing task: {task_name}...")
            tasks_state[task_idx]["status"] = "Running"
            self._save_state(task_name, tasks_state)
            
            # Simulate a build failure and recovery during "unit_testing" to test Self-Healing
            if task_name == "unit_testing":
                print("[ERROR] Build failed: SyntaxError in tests/test_auth.py: Line 12 - missing close parenthesis.")
                tasks_state[task_idx]["status"] = "Failed"
                self._save_state(task_name, tasks_state)
                
                # Trigger Autonomous Recovery Engine
                recovery = AutonomousRecoveryEngine(self.workspace_path)
                rca = recovery.perform_rca("SyntaxError: unmatched ')' in test_auth.py line 12")
                fixed = recovery.apply_remediation(rca)
                
                if fixed:
                    tasks_state[task_idx]["status"] = "Completed"
                    self._save_state(task_name, tasks_state)
                    print(f"Task {task_name} successfully recovered and completed.")
                else:
                    print(f"Task {task_name} failed recovery.")
            else:
                # Normal successful execution
                time.sleep(0.1)
                tasks_state[task_idx]["status"] = "Completed"
                self._save_state(task_name, tasks_state)
                print(f"Task {task_name} completed.")
                
        return True

                
        return True
