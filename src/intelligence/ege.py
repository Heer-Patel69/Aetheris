import os
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

class EngineeringGraphEngine:
    """Digital Twin Dependency Graph mapping requirements, modules, and tests (SPEC-006)."""
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()
        self.graph_file = self.workspace_path / ".aetheris" / "execution" / "architecture.graph.json"
        self._load_graph()

    def _load_graph(self) -> None:
        if self.graph_file.exists():
            try:
                data = json.loads(self.graph_file.read_text(encoding="utf-8"))
                self.nodes = data.get("nodes", [])
                self.edges = data.get("edges", [])
            except Exception:
                self.nodes = []
                self.edges = []
        else:
            self.nodes = []
            self.edges = []

    def _save_graph(self) -> None:
        try:
            self.graph_file.parent.mkdir(parents=True, exist_ok=True)
            data = {"nodes": self.nodes, "edges": self.edges}
            self.graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def add_node(self, node_id: str, type: str, metadata: dict = None) -> None:
        """Registers a structural artifact node in the project graph."""
        # Prevent duplicates
        if not any(n["id"] == node_id for n in self.nodes):
            self.nodes.append({
                "id": node_id,
                "type": type,
                "metadata": metadata or {}
            })
            self._save_graph()

    def add_edge(self, source: str, target: str, relationship: str) -> None:
        """Draws a directed dependency reference between two nodes."""
        if not any(e["source"] == source and e["target"] == target for e in self.edges):
            self.edges.append({
                "source": source,
                "target": target,
                "relationship": relationship
            })
            self._save_graph()

    def detect_cycles(self) -> List[str]:
        """Detects circular dependency paths via DFS back-edge check."""
        adj = {n["id"]: [] for n in self.nodes}
        for e in self.edges:
            src = e["source"]
            dst = e["target"]
            if src in adj and dst in adj:
                adj[src].append(dst)

        cycles = []
        visited = {} # None=unvisited, 0=visiting, 1=visited
        path = []

        def dfs(u):
            visited[u] = 0 # visiting
            path.append(u)
            for v in adj[u]:
                if visited.get(v) == 0:
                    idx = path.index(v)
                    cycle_path = " -> ".join(path[idx:]) + f" -> {v}"
                    cycles.append(cycle_path)
                elif v not in visited:
                    dfs(v)
            path.pop()
            visited[u] = 1 # visited

        for node in adj:
            if node not in visited:
                dfs(node)

        return cycles

    def get_impacted_nodes(self, node_id: str) -> List[str]:
        """Runs a BFS traversal backwards along reference edges to list impacted nodes."""
        # Build inverted adjacency list
        incoming = {n["id"]: [] for n in self.nodes}
        for e in self.edges:
            src = e["source"]
            dst = e["target"]
            if src in incoming and dst in incoming:
                # Invert relation: if src depends on dst, dst impacts src
                incoming[dst].append(src)

        if node_id not in incoming:
            return []

        impacted = []
        queue = [node_id]
        visited = {node_id}

        while queue:
            curr = queue.pop(0)
            for neighbor in incoming[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    impacted.append(neighbor)

        return impacted

    def get_isolated_nodes(self) -> List[str]:
        """Finds dead-code/isolated artifacts with zero connections."""
        connected = set()
        for e in self.edges:
            connected.add(e["source"])
            connected.add(e["target"])
            
        return [n["id"] for n in self.nodes if n["id"] not in connected]
