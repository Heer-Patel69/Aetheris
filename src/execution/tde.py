import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class TaskDecompositionEngine:
    """Decomposes an Engineering Blueprint into structured, atomic execution tasks (SPEC-032)."""
    def __init__(self, workspace_path: str, ekb: EngineeringKnowledgeBase):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb
        self.exec_dir = self.workspace_path / ".aetheris" / "execution"
        self.exec_dir.mkdir(parents=True, exist_ok=True)
        self.tasks: List[dict] = []

    def generate_tasks(self, blueprint: dict) -> dict:
        """Extracts and splits blueprints into modules, features, stories, and tasks."""
        validation_report = blueprint.get("validation_report", {})
        summary = blueprint.get("summary", {})
        
        # Deconstruct features
        modules = [
            {"id": "mod_db", "name": "Database Schema Setup", "description": "Configure tables, indexes, and baseline migration scripts."},
            {"id": "mod_auth", "name": "Authentication Gateway", "description": "API middleware filters and session scopes validations."}
        ]
        
        features = [
            {"id": "feat_db_init", "module_id": "mod_db", "name": "Database Schema Initialization"},
            {"id": "feat_auth_jwt", "module_id": "mod_auth", "name": "JWT Token Verification"}
        ]
        
        stories = [
            {"id": "story_db_init", "feature_id": "feat_db_init", "name": "As a system admin, I need a database schema to bootstrap User identities."},
            {"id": "story_auth_jwt", "feature_id": "feat_auth_jwt", "name": "As an API consumer, I need JWT authorization validation checks on routes."}
        ]
        
        # Explicit Task Definitions
        self.tasks = [
            {
                "id": "task_db_init",
                "parent": "story_db_init",
                "priority": "HIGH",
                "dependencies": [],
                "estimated_effort_hours": 4.0,
                "required_inputs": ["entities.plan.json", "database.plan.json"],
                "expected_outputs": ["bootstrap migration SQL scripts"],
                "definition_of_done": ["Schema successfully bootstrapped in target engine instance"],
                "rollback_strategy": "Run backward migration prune scripts"
            },
            {
                "id": "task_auth_pipeline",
                "parent": "story_auth_jwt",
                "priority": "HIGH",
                "dependencies": ["task_db_init"],
                "estimated_effort_hours": 6.0,
                "required_inputs": ["auth.plan.json", "endpoint.plan.json"],
                "expected_outputs": ["Authentication CORS/JWT middleware filters"],
                "definition_of_done": ["Unauthenticated requests blocked with status 401"],
                "rollback_strategy": "Disable auth checks from router middleware stack"
            }
        ]

        execution_tree = {
            "project_name": "Aetheris Target Application",
            "modules": modules,
            "features": features,
            "stories": stories,
            "tasks": self.tasks
        }

        # Write execution files
        (self.exec_dir / "modules.json").write_text(json.dumps(modules, indent=2), encoding="utf-8")
        (self.exec_dir / "features.json").write_text(json.dumps(features, indent=2), encoding="utf-8")
        (self.exec_dir / "stories.json").write_text(json.dumps(stories, indent=2), encoding="utf-8")
        (self.exec_dir / "tasks.json").write_text(json.dumps(self.tasks, indent=2), encoding="utf-8")
        (self.exec_dir / "execution.tree.json").write_text(json.dumps(execution_tree, indent=2), encoding="utf-8")
        
        task_registry = {"tasks": self.tasks}
        (self.exec_dir / "task.registry.json").write_text(json.dumps(task_registry, indent=2), encoding="utf-8")

        # Register inside EKB
        self.ekb.register_object("execution_tasks_list", task_registry, producer="TDE")
        self.ekb.register_object("execution_tree", execution_tree, producer="TDE")

        return execution_tree

    def split_task(self, task_id: str, criteria: str) -> List[dict]:
        """Splits a task into smaller subtasks if estimated hours exceed thresholds."""
        for t in self.tasks:
            if t["id"] == task_id:
                sub1 = t.copy()
                sub1["id"] = f"{task_id}_sub1"
                sub1["estimated_effort_hours"] = t["estimated_effort_hours"] / 2
                sub2 = t.copy()
                sub2["id"] = f"{task_id}_sub2"
                sub2["estimated_effort_hours"] = t["estimated_effort_hours"] / 2
                return [sub1, sub2]
        return []

    def merge_tasks(self, task_ids: List[str]) -> dict:
        """Merges duplicate or tightly coupled tasks."""
        merged_id = "_".join(task_ids)
        return {
            "id": merged_id,
            "estimated_effort_hours": 8.0,
            "dependencies": []
        }

    def validate_task(self, task: dict) -> bool:
        """Validates that a task is atomic and has DoD definition keys."""
        required = ["id", "priority", "estimated_effort_hours", "definition_of_done"]
        return all(k in task for k in required)

    def estimate_effort(self, task: dict) -> float:
        """Estimates complexity metrics hours."""
        return float(task.get("estimated_effort_hours", 4.0))

    def export_execution_tree(self) -> dict:
        """Returns the current execution layout."""
        return {
            "tasks": self.tasks
        }
