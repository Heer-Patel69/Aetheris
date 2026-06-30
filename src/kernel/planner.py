import os
import json
import time
from pathlib import Path

try:
    from kernel.goal_manager import EngineeringKnowledgeBase
except ImportError:
    class EngineeringKnowledgeBase:
        def __init__(self, workspace_path):
            self.workspace_path = Path(workspace_path).resolve()
            self.knowledge_dir = self.workspace_path / ".aetheris" / "knowledge"
        def load_artifact(self, name: str) -> dict:
            dest_file = self.knowledge_dir / f"{name}.json"
            if not dest_file.exists():
                return {}
            try:
                return json.loads(dest_file.read_text(encoding="utf-8"))
            except Exception:
                return {}

class EngineeringPlanner:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = EngineeringKnowledgeBase(self.workspace_path)
        self.execution_dir = self.workspace_path / ".aetheris"
        
    def build_task_dag(self, blueprint=None):
        """
        Creates a list of tasks sorted topologically by their dependencies.
        Kept for backward compatibility.
        """
        # If blueprint is not passed, load from EKB
        if not blueprint:
            blueprint = self.ekb.load_artifact("universal.blueprint") or {}
        
        # Load completeness report
        completeness = self.ekb.load_artifact("completeness.report") or {}
        missing_requirements = completeness.get("missing_requirements", [])
        
        inferred_subsystems = blueprint.get("inferred_subsystems", [])
        
        # Default dependency rules
        dependency_rules = {
            "database_migrations": [],
            "authentication": ["database_migrations"],
            "api_controllers": ["database_migrations", "authentication"],
            "frontend_views": ["api_controllers"],
            "unit_testing": ["api_controllers", "frontend_views"],
            "dockerization": ["database_migrations"],
            "deployment_pipelines": ["unit_testing", "dockerization"]
        }
        
        # Filter inferred subsystems to ensure we only process existing ones
        subsystems = list(inferred_subsystems)
        # If we have missing requirements from completeness, ensure matching subsystems are included
        for missing in missing_requirements:
            if "database" in missing.lower() and "database_migrations" not in subsystems:
                subsystems.append("database_migrations")
            if "auth" in missing.lower() and "authentication" not in subsystems:
                subsystems.append("authentication")
            if "container" in missing.lower() or "docker" in missing.lower() and "dockerization" not in subsystems:
                subsystems.append("dockerization")
            if "ci/cd" in missing.lower() or "pipeline" in missing.lower() and "deployment_pipelines" not in subsystems:
                subsystems.append("deployment_pipelines")
                
        # Remove duplicates while preserving order
        unique_subsystems = []
        for s in subsystems:
            if s not in unique_subsystems:
                unique_subsystems.append(s)
                
        # Construct graph nodes and edges
        nodes = []
        edges = []
        for system in unique_subsystems:
            nodes.append(system)
            deps = dependency_rules.get(system, [])
            for dep in deps:
                if dep in unique_subsystems:
                    edges.append((dep, system)) # dep -> system (system depends on dep)
                    
        # Perform topological sort
        sorted_tasks = self._topological_sort(nodes, edges)
        
        # Build waves for concurrency
        waves = self._build_concurrency_waves(nodes, edges)
        
        # Save output plans
        self._save_execution_artifacts(sorted_tasks, nodes, edges, waves, blueprint.get("vision", ""))
        
        print(f"Topological Task DAG compiled: {' -> '.join(sorted_tasks)}")
        return sorted_tasks

    def plan(self):
        """
        Main runner to compile and save execution plans.
        """
        return self.build_task_dag()

    def _topological_sort(self, nodes, edges):
        adj = {n: [] for n in nodes}
        in_degree = {n: 0 for n in nodes}
        for src, dst in edges:
            if src in adj and dst in adj:
                adj[src].append(dst)
                in_degree[dst] += 1
                
        queue = [n for n in nodes if in_degree[n] == 0]
        queue.sort() # For determinism
        
        sorted_nodes = []
        while queue:
            u = queue.pop(0)
            sorted_nodes.append(u)
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        # Append cycle remnants just in case
        for n in nodes:
            if n not in sorted_nodes:
                sorted_nodes.append(n)
        return sorted_nodes

    def _build_concurrency_waves(self, nodes, edges):
        adj = {n: [] for n in nodes}
        in_degree = {n: 0 for n in nodes}
        for src, dst in edges:
            if src in adj and dst in adj:
                adj[src].append(dst)
                in_degree[dst] += 1
                
        remaining = set(nodes)
        waves = []
        while remaining:
            wave = [n for n in remaining if in_degree[n] == 0]
            if not wave:
                waves.append(sorted(list(remaining)))
                break
            wave.sort()
            waves.append(wave)
            for u in wave:
                remaining.remove(u)
                for v in adj[u]:
                    if v in remaining:
                        in_degree[v] -= 1
        return waves

    def _save_execution_artifacts(self, sorted_tasks, nodes, edges, waves, vision):
        self.execution_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. execution.plan.json
        plan_data = {
            "goal": vision or "Autonomous execution",
            "tasks": [
                {
                    "id": f"task:{task}",
                    "name": task.replace("_", " ").title(),
                    "status": "PENDING",
                    "dependencies": [f"task:{src}" for src, dst in edges if dst == task]
                }
                for task in sorted_tasks
            ],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        (self.execution_dir / "execution.plan.json").write_text(json.dumps(plan_data, indent=2), encoding="utf-8")
        
        # 2. execution.graph.json
        graph_nodes = []
        for n in nodes:
            graph_nodes.append({
                "id": f"task:{n}",
                "type": "Task",
                "metadata": {"name": n.replace("_", " ").title()}
            })
        graph_edges = []
        for src, dst in edges:
            graph_edges.append({
                "source": f"task:{src}",
                "target": f"task:{dst}",
                "relationship": "depends_on"
            })
        graph_data = {
            "nodes": graph_nodes,
            "edges": graph_edges
        }
        (self.execution_dir / "execution.graph.json").write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
        
        # 3. execution.queue.json
        queue_data = {
            "waves": [[f"task:{t}" for t in wave] for wave in waves]
        }
        (self.execution_dir / "execution.queue.json").write_text(json.dumps(queue_data, indent=2), encoding="utf-8")
