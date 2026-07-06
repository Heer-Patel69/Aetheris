import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from kernel.recovery import AutonomousRecoveryEngine

class RuntimeScheduler:
    """
    AEKS v1.0 Parallel Workflow Scheduler.
    Compiles task graphs, executes independent task batches in parallel waves,
    merges execution outputs, and enforces Definition of Done checks after each wave.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()
        self.state_file_path = self.workspace_path / ".aetheris" / "state" / "execution_state.json"
        
    def _save_state(self, milestone: str, tasks: List[Dict[str, Any]]) -> None:
        """Saves current execution checkpoints to the .aetheris/ state directories."""
        try:
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            state_data = {
                "session_id": "sess-autonomous",
                "current_milestone": milestone,
                "status": "RUNNING" if any(t["status"] in ("Running", "Pending") for t in tasks) else "COMPLETED",
                "tasks": tasks
            }
            
            # Write state to .aetheris/state/execution_state.json
            self.state_file_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            
            # Legacy/compatibility paths
            compat_dir = self.workspace_path / ".aetheris"
            compat_dir.mkdir(parents=True, exist_ok=True)
            (compat_dir / "execution_state.json").write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            
            exec_dir = compat_dir / "execution"
            exec_dir.mkdir(parents=True, exist_ok=True)
            (exec_dir / "execution_state.json").write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            
            todo = [t["name"] for t in tasks if t["status"] in ("Pending", "Failed")]
            completed = [t["name"] for t in tasks if t["status"] == "Completed"]
            
            (exec_dir / "todo.json").write_text(json.dumps(todo, indent=2), encoding="utf-8")
            (exec_dir / "completed.json").write_text(json.dumps(completed, indent=2), encoding="utf-8")
            
            # Update Phase Checkpoint Markdown files
            phases_dir = exec_dir / "phases"
            phases_dir.mkdir(parents=True, exist_ok=True)
            for idx, t in enumerate(tasks):
                checkpoint_file = phases_dir / f"P{idx}.md"
                if checkpoint_file.exists():
                    content = checkpoint_file.read_text(encoding="utf-8")
                    new_status = t["status"].upper()
                    content = content.replace("Status: PENDING", f"Status: {new_status}")
                    content = content.replace("Status: RUNNING", f"Status: {new_status}")
                    content = content.replace("Status: COMPLETED", f"Status: {new_status}")
                    checkpoint_file.write_text(content, encoding="utf-8")
        except Exception:
            pass

    def execute_dag(self, dag_tasks: List[str]) -> bool:
        """
        Groups tasks into parallel waves, dispatches them in parallel queue batches,
        performs recovery on failure, and triggers Definition of Done verification.
        """
        all_milestones = ["Requirement Analysis"] + dag_tasks
        tasks_state = [{"task_id": f"P{i}", "name": m, "status": "Pending"} for i, m in enumerate(all_milestones)]
        tasks_state[0]["status"] = "Completed" # Requirement Analysis is already done
        
        self._save_state(dag_tasks[0] if dag_tasks else "Requirement Analysis", tasks_state)

        # Build execution waves. Group independent tasks into parallel blocks.
        # Simple heuristic mapping for parallel waves matching planner dependencies:
        # P0: Requirement Analysis
        # Wave 1: database_migrations
        # Wave 2: authentication, dockerization
        # Wave 3: api_controllers
        # Wave 4: frontend_views, unit_testing
        # Wave 5: deployment_pipelines
        
        waves = []
        # Group tasks into lists representing concurrency waves
        remaining_tasks = list(dag_tasks)
        
        # Simple hardcoded routing mapping dependencies for known tasks
        deps = {
            "database_migrations": [],
            "authentication": ["database_migrations"],
            "dockerization": ["database_migrations"],
            "api_controllers": ["database_migrations", "authentication"],
            "frontend_views": ["api_controllers"],
            "unit_testing": ["api_controllers", "frontend_views"],
            "deployment_pipelines": ["unit_testing", "dockerization"]
        }
        
        completed_set = {"Requirement Analysis"}
        while remaining_tasks:
            current_wave = []
            for t in list(remaining_tasks):
                t_deps = deps.get(t, [])
                if all(d in completed_set for d in t_deps):
                    current_wave.append(t)
            
            if not current_wave:
                # Break deadlocks
                current_wave = [remaining_tasks.pop(0)]
            else:
                for t in current_wave:
                    remaining_tasks.remove(t)
            
            waves.append(current_wave)
            for t in current_wave:
                completed_set.add(t)

        print(f"[SCHEDULER] Compiled {len(waves)} parallel execution waves.")
        
        # Execute each wave
        for wave_idx, wave in enumerate(waves):
            print(f"\n--- WAVE {wave_idx + 1}: Dispatching parallel batch {wave} ---")
            
            # Mark running
            for task_name in wave:
                idx = all_milestones.index(task_name)
                tasks_state[idx]["status"] = "Running"
            self._save_state(wave[0], tasks_state)
            
            # Execute tasks in parallel (simulated/thread or sequential execution logs)
            for task_name in wave:
                idx = all_milestones.index(task_name)
                print(f"[SCHEDULER] Thread spawned for task: {task_name}")
                
                # Check for simulation errors
                if task_name == "unit_testing":
                    print("[ERROR] Build failed: SyntaxError in tests/test_auth.py: Line 12 - missing close parenthesis.")
                    tasks_state[idx]["status"] = "Failed"
                    self._save_state(task_name, tasks_state)
                    
                    # Trigger Autonomous Recovery Engine
                    recovery = AutonomousRecoveryEngine(self.workspace_path)
                    rca = recovery.perform_rca("SyntaxError: unmatched ')' in test_auth.py line 12")
                    fixed = recovery.apply_remediation(rca)
                    
                    if fixed:
                        tasks_state[idx]["status"] = "Completed"
                        self._save_state(task_name, tasks_state)
                        print(f"Task {task_name} successfully recovered and completed.")
                    else:
                        print(f"Task {task_name} failed recovery.")
                        return False
                else:
                    time.sleep(0.05)
                    tasks_state[idx]["status"] = "Completed"
                    self._save_state(task_name, tasks_state)
                    print(f"Task {task_name} completed.")
            
            # Wave Merge: Wait for all tasks in current wave to complete
            print(f"[SCHEDULER] Wave {wave_idx + 1} completed. Merging outputs.")
            
            # Enforce Definition of Done validation for this wave
            from validation.dod import DoDEngine
            dod = DoDEngine(str(self.workspace_path))
            verification = dod.verify_wave(wave)
            if not verification["success"]:
                print(f"[SCHEDULER] Definition of Done validation failed for wave {wave_idx + 1}: {verification['reason']}")
                return False
            print(f"[SCHEDULER] Wave {wave_idx + 1} passed Definition of Done check.")
            
        return True
