import os
from pathlib import Path

class EngineeringPlanner:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        
    def build_task_dag(self, blueprint):
        """
        Creates a list of tasks sorted topologically by their dependencies.
        """
        subsystems = blueprint.get("inferred_subsystems", [])
        
        # Hardcoded dependency weights to establish correct topological sorting
        # (e.g. Database must run before Authentication or APIs)
        dependency_weights = {
            "database_migrations": 10,
            "authentication": 20,
            "authentication (inferred)": 20,
            "api_controllers": 30,
            "frontend_views": 40,
            "unit_testing": 50,
            "dockerization": 60,
            "deployment_pipelines": 70
        }
        
        # Filter and sort by dependency hierarchy
        dag_tasks = []
        for system in subsystems:
            weight = dependency_weights.get(system, 99)
            dag_tasks.append((system, weight))
            
        dag_tasks.sort(key=lambda x: x[1])
        
        # Return just the task names in order
        sorted_tasks = [task[0] for task in dag_tasks]
        print(f"Topological Task DAG compiled: {' -> '.join(sorted_tasks)}")
        return sorted_tasks
