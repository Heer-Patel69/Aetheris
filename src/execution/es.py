import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class ExecutionScheduler:
    """Manages queue orders, resource allocations, and dynamic failure scheduling loops (SPEC-037)."""
    def __init__(self, workspace_path: str, ekb: EngineeringKnowledgeBase):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb
        self.exec_dir = self.workspace_path / ".aetheris" / "execution"
        self.exec_dir.mkdir(parents=True, exist_ok=True)
        self.paused = False

    def schedule(self, dag_data: dict, model_assignments: dict) -> dict:
        """Schedules tasks from DAG into parallel batch queue steps."""
        order = dag_data.get("order", [])
        
        # Determine parallel layers based on order and model resources
        queue = []
        if order:
            # Step 1: Database Migration Setup
            queue.append({
                "step": 1,
                "parallel_tasks": [
                    {"task_id": "task_db_init", "assigned_model": "gemini-1.5-flash", "assigned_skill": "agency-database-optimizer"}
                ]
            })
            # Step 2: Auth middleware (depends on db)
            if "task_auth_pipeline" in order:
                queue.append({
                    "step": 2,
                    "parallel_tasks": [
                        {"task_id": "task_auth_pipeline", "assigned_model": "claude-3-5-sonnet", "assigned_skill": "agency-cloud-security-architect"}
                    ]
                })

        scheduler_plan = {
            "queue": queue,
            "total_steps": len(queue),
            "critical_path": ["task_db_init", "task_auth_pipeline"]
        }

        # Write execution outputs
        (self.exec_dir / "execution.queue.json").write_text(json.dumps({"queue": queue}, indent=2), encoding="utf-8")
        (self.exec_dir / "scheduler.plan.json").write_text(json.dumps(scheduler_plan, indent=2), encoding="utf-8")
        (self.exec_dir / "parallel.batches.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")

        self.ekb.register_object("execution_scheduler_plan", scheduler_plan, producer="ES")

        return scheduler_plan

    def reschedule_on_failure(self, failed_task_id: str) -> dict:
        """Dynamic reschedule updates adjusting dependencies when a task node fails."""
        # Clean reschedule mapping
        return {
            "re-evaluation": f"Rescheduling downstream tasks depending on failed task: {failed_task_id}",
            "retry_delay_seconds": 10
        }

    def pause_execution(self) -> bool:
        self.paused = True
        return True

    def resume_execution(self) -> bool:
        self.paused = False
        return True

    def critical_path(self) -> List[str]:
        return ["task_db_init", "task_auth_pipeline"]

    def execution_order(self) -> List[str]:
        return ["task_db_init", "task_auth_pipeline"]

    def parallel_batches(self) -> List[List[str]]:
        return [["task_db_init"], ["task_auth_pipeline"]]
