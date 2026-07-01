import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class DependencyGraphBuilder:
    """Transforms decomposed engineering tasks into cycle-free Directed Acyclic Graphs (SPEC-033)."""
    def __init__(self, workspace_path: str, ekb: EngineeringKnowledgeBase):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb
        self.exec_dir = self.workspace_path / ".aetheris" / "execution"
        self.exec_dir.mkdir(parents=True, exist_ok=True)
        self.adjacency_list: Dict[str, List[str]] = {}
        self.task_map: Dict[str, dict] = {}

    def build_graph(self, tasks: List[dict]) -> dict:
        """Constructs graph nodes and dependency edges."""
        self.adjacency_list = {}
        self.task_map = {t["id"]: t for t in tasks}

        nodes = []
        edges = []

        for t in tasks:
            tid = t["id"]
            self.adjacency_list[tid] = []
            nodes.append({"id": tid, "label": tid})
            
            # Map depends_on edges
            for dep in t.get("dependencies", []):
                self.adjacency_list[tid].append(dep)
                edges.append({"source": dep, "target": tid, "type": "depends_on"})

        graph_data = {
            "nodes": nodes,
            "edges": edges
        }

        # Save to disk
        (self.exec_dir / "dependency.graph.json").write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
        
        # Check cycles
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"CRITICAL DEPENDENCY CYCLE DETECTED: {cycles}")

        # Compute topological order
        topo_order = self.get_topological_order()
        (self.exec_dir / "execution.dag.json").write_text(json.dumps({"order": topo_order}, indent=2), encoding="utf-8")

        # Compile parallel groups
        parallel_groups = self.get_parallel_groups()
        (self.exec_dir / "parallel.groups.json").write_text(json.dumps(parallel_groups, indent=2), encoding="utf-8")

        # Critical path
        critical_path = self.calculate_critical_path()
        (self.exec_dir / "critical.path.json").write_text(json.dumps(critical_path, indent=2), encoding="utf-8")

        # Register in EKB
        self.ekb.register_object("execution_dag", graph_data, producer="DGB")
        self.ekb.register_object("topological_order", {"order": topo_order}, producer="DGB")

        return graph_data

    def detect_cycles(self) -> List[List[str]]:
        """Detects cycles in the dependency graph using DFS coloring."""
        visited: Dict[str, int] = {} # 0: unvisited, 1: visiting, 2: visited
        cycles = []
        path: List[str] = []

        def dfs(node: str) -> bool:
            visited[node] = 1
            path.append(node)
            for neighbor in self.adjacency_list.get(node, []):
                if neighbor not in visited or visited[neighbor] == 0:
                    if dfs(neighbor):
                        return True
                elif visited[neighbor] == 1:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:])
                    return True
            path.pop()
            visited[node] = 2
            return False

        for node in self.adjacency_list:
            if node not in visited or visited[node] == 0:
                if dfs(node):
                    return cycles
        return []

    def get_topological_order(self) -> List[str]:
        """Runs a topological sort using DFS."""
        visited: Set[str] = set()
        order = []

        def dfs(node: str):
            visited.add(node)
            for neighbor in self.adjacency_list.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
            order.append(node)

        for node in self.adjacency_list:
            if node not in visited:
                dfs(node)
        return order

    def calculate_critical_path(self) -> List[str]:
        """Calculates critical path using early/late scheduling parameters."""
        order = self.get_topological_order()
        early_start = {n: 0.0 for n in self.adjacency_list}
        early_finish = {n: float(self.task_map[n]["estimated_effort_hours"]) for n in self.adjacency_list}

        # Forward pass
        for node in order:
            duration = float(self.task_map[node]["estimated_effort_hours"])
            deps = self.adjacency_list.get(node, [])
            if deps:
                early_start[node] = max(early_finish[d] for d in deps)
                early_finish[node] = early_start[node] + duration

        # Backward pass
        late_finish = {n: max(early_finish.values()) for n in self.adjacency_list}
        late_start = {n: late_finish[n] - float(self.task_map[n]["estimated_effort_hours"]) for n in self.adjacency_list}

        for node in reversed(order):
            dependents = [n for n in self.adjacency_list if node in self.adjacency_list[n]]
            if dependents:
                late_finish[node] = min(late_start[d] for d in dependents)
                late_start[node] = late_finish[node] - float(self.task_map[node]["estimated_effort_hours"])

        # Critical path nodes have zero slack
        critical_path = [node for node in order if abs(early_start[node] - late_start[node]) < 1e-5]
        return critical_path

    def get_parallel_groups(self) -> List[List[str]]:
        """Groups tasks into layers that can be executed in parallel (level-order scheduling)."""
        forward_adj: Dict[str, List[str]] = {n: [] for n in self.adjacency_list}
        in_degree = {n: 0 for n in self.adjacency_list}
        
        for node, deps in self.adjacency_list.items():
            for dep in deps:
                forward_adj[dep].append(node)
                in_degree[node] += 1

        queue = [n for n in self.adjacency_list if in_degree[n] == 0]
        groups = []

        while queue:
            groups.append(list(queue))
            next_queue = []
            for node in queue:
                for dependent in forward_adj[node]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)
            queue = next_queue
        return groups
