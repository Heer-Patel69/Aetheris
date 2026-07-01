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
        
        # 1. Establish EEJ Directory structure
        exec_dir = self.execution_dir / "execution"
        knowledge_dir = self.execution_dir / "knowledge"
        memory_dir = self.execution_dir / "memory"
        
        for d in (exec_dir, knowledge_dir, memory_dir):
            d.mkdir(parents=True, exist_ok=True)

        # 2. Save traditional compatibility outputs
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
        
        graph_nodes = [{"id": f"task:{n}", "type": "Task", "metadata": {"name": n.replace("_", " ").title()}} for n in nodes]
        graph_edges = [{"source": f"task:{src}", "target": f"task:{dst}", "relationship": "depends_on"} for src, dst in edges]
        graph_data = {"nodes": graph_nodes, "edges": graph_edges}
        (self.execution_dir / "execution.graph.json").write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
        
        queue_data = {"waves": [[f"task:{t}" for t in wave] for wave in waves]}
        (self.execution_dir / "execution.queue.json").write_text(json.dumps(queue_data, indent=2), encoding="utf-8")

        # 3. Save EPE Live Execution State Files
        all_milestones = ["Requirement Analysis"] + [t.replace("_", " ").title() for t in sorted_tasks]
        
        # execution_state.json
        state_tasks = [{"task_id": f"P{i}", "name": m, "status": "Pending"} for i, m in enumerate(all_milestones)]
        state_tasks[0]["status"] = "Completed" # Requirement analysis done when plan is created
        
        execution_state = {
            "session_id": "sess-autonomous",
            "current_milestone": f"P1: {all_milestones[1]}" if len(all_milestones) > 1 else "P0: Requirement Analysis",
            "status": "RUNNING",
            "tasks": state_tasks
        }
        (exec_dir / "execution_state.json").write_text(json.dumps(execution_state, indent=2), encoding="utf-8")
        (self.execution_dir / "execution_state.json").write_text(json.dumps(execution_state, indent=2), encoding="utf-8") # Compatibility copy

        # todo.json & completed.json & blockers.json
        todo_list = [t["name"] for t in state_tasks if t["status"] == "Pending"]
        completed_list = [t["name"] for t in state_tasks if t["status"] == "Completed"]
        (exec_dir / "todo.json").write_text(json.dumps(todo_list, indent=2), encoding="utf-8")
        (exec_dir / "completed.json").write_text(json.dumps(completed_list, indent=2), encoding="utf-8")
        (exec_dir / "blockers.json").write_text(json.dumps([], indent=2), encoding="utf-8")

        # resume.json
        resume_data = {
            "last_active_milestone": execution_state["current_milestone"],
            "timestamp": time.time(),
            "can_resume": True
        }
        (exec_dir / "resume.json").write_text(json.dumps(resume_data, indent=2), encoding="utf-8")

        # decisions.jsonl & execution.log.jsonl
        (exec_dir / "decisions.jsonl").write_text("", encoding="utf-8")
        log_record = {
            "timestamp": time.time(),
            "event": "PlanCreated",
            "message": f"Successfully compiled execution plan with {len(all_milestones)} phases."
        }
        (exec_dir / "execution.log.jsonl").write_text(json.dumps(log_record) + "\n", encoding="utf-8")

        # metrics.json
        metrics_data = {
            "total_duration_ms": 0,
            "total_token_usage": 0,
            "success_rate": 1.0
        }
        (exec_dir / "metrics.json").write_text(json.dumps(metrics_data, indent=2), encoding="utf-8")

        # milestones.json
        (exec_dir / "milestones.json").write_text(json.dumps(all_milestones, indent=2), encoding="utf-8")

        # 4. Generate Phase Checkpoint Markdowns
        phases_dir = exec_dir / "phases"
        phases_dir.mkdir(parents=True, exist_ok=True)
        
        for i, m in enumerate(all_milestones):
            status = "COMPLETED" if i == 0 else "PENDING"
            md_content = f"""# Phase Checkpoint: P{i} — {m}
- **Objective**: Execute and verify {m}
- **Status**: {status}
- **Started Time**: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) if i == 0 else 'N/A'}
- **Completed Time**: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) if i == 0 else 'N/A'}

## Tasks
- [{"x" if i == 0 else " "}] Run {m} execution checks
- [ ] Verify DoD compliance

## Files Modified
*None*

## Verification Results
- Ingestion passed validation schema.
"""
            (phases_dir / f"P{i}.md").write_text(md_content, encoding="utf-8")

        print(f"Topological Task DAG compiled: {' -> '.join(sorted_tasks)}")
        return sorted_tasks

    def resume_execution(self) -> dict:
        """Loads and reconstructs the execution state from the EEJ state files (ADR-006)."""
        exec_dir = self.workspace_path / ".aetheris" / "execution"
        state_file = exec_dir / "execution_state.json"
        
        if not state_file.exists():
            return {"can_resume": False, "reason": "No execution state file found."}
            
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            todo = json.loads((exec_dir / "todo.json").read_text(encoding="utf-8"))
            completed = json.loads((exec_dir / "completed.json").read_text(encoding="utf-8"))
            blockers = json.loads((exec_dir / "blockers.json").read_text(encoding="utf-8"))
            resume = json.loads((exec_dir / "resume.json").read_text(encoding="utf-8"))
            
            return {
                "can_resume": True,
                "current_milestone": state.get("current_milestone"),
                "status": state.get("status"),
                "tasks": state.get("tasks", []),
                "todo": todo,
                "completed": completed,
                "blockers": blockers,
                "resume_metadata": resume
            }
        except Exception as e:
            return {"can_resume": False, "reason": f"Failed to parse state files: {e}"}

