import os
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

class EngineeringGraphEngine:
    """
    AEKS v1.0 Engineering Intelligence Graph Engine.
    Exposes and builds the queryable digital twin connecting 17 subgraphs:
    Business -> Requirement -> Product -> Repository -> Dependency -> Technology ->
    Architecture -> Database -> API -> Security -> Skill -> RFC -> SPEC ->
    Execution -> Benchmark -> Decision -> Memory.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()
        self.graph_file = self.workspace_path / ".aetheris" / "graphs" / "intelligence.graph.json"
        self.compat_graph_file = self.workspace_path / ".aetheris" / "execution" / "architecture.graph.json"
        
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self._load_graph()

    def _load_graph(self) -> None:
        target = self.graph_file if self.graph_file.exists() else self.compat_graph_file
        if target.exists():
            try:
                data = json.loads(target.read_text(encoding="utf-8"))
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
            self.compat_graph_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {"nodes": self.nodes, "edges": self.edges}
            serialized = json.dumps(data, indent=2),
            # Extract string from tuple if single item tuple returned
            serialized_str = serialized[0] if isinstance(serialized, tuple) else serialized
            
            self.graph_file.write_text(serialized_str, encoding="utf-8")
            self.compat_graph_file.write_text(serialized_str, encoding="utf-8")
        except Exception:
            pass

    def add_subgraph_node(self, subgraph: str, node_id: str, type: str, metadata: dict = None) -> None:
        """Registers an artifact node in a specific subgraph of the digital twin."""
        meta = metadata or {}
        meta["subgraph"] = subgraph
        
        # Prevent duplicate nodes
        for node in self.nodes:
            if node["id"] == node_id:
                node["metadata"].update(meta)
                self._save_graph()
                return
                
        self.nodes.append({
            "id": node_id,
            "type": type,
            "metadata": meta
        })
        self._save_graph()

    def add_node(self, node_id: str, type: str, metadata: dict = None) -> None:
        """Legacy helper matching AEOS class signatures, registering node in 'architecture'."""
        self.add_subgraph_node("architecture", node_id, type, metadata)

    def add_edge(self, source: str, target: str, relationship: str) -> None:
        """Draws a directed reference relationship between two nodes across subgraphs."""
        if not any(e["source"] == source and e["target"] == target for e in self.edges):
            self.edges.append({
                "source": source,
                "target": target,
                "relationship": relationship
            })
            self._save_graph()

    def get_subgraph_nodes(self, subgraph: str) -> List[Dict[str, Any]]:
        """Returns all nodes registered under a specific subgraph."""
        return [n for n in self.nodes if n.get("metadata", {}).get("subgraph") == subgraph]

    def detect_cycles(self) -> List[str]:
        adj = {n["id"]: [] for n in self.nodes}
        for e in self.edges:
            src = e["source"]
            dst = e["target"]
            if src in adj and dst in adj:
                adj[src].append(dst)

        cycles = []
        visited = {}
        path = []

        def dfs(u):
            visited[u] = 0
            path.append(u)
            for v in adj[u]:
                if visited.get(v) == 0:
                    idx = path.index(v)
                    cycle_path = " -> ".join(path[idx:]) + f" -> {v}"
                    cycles.append(cycle_path)
                elif v not in visited:
                    dfs(v)
            path.pop()
            visited[u] = 1

        for node in adj:
            if node not in visited:
                dfs(node)
        return cycles

    def get_impacted_nodes(self, node_id: str) -> List[str]:
        incoming = {n["id"]: [] for n in self.nodes}
        for e in self.edges:
            src = e["source"]
            dst = e["target"]
            if src in incoming and dst in incoming:
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
        connected = set()
        for e in self.edges:
            connected.add(e["source"])
            connected.add(e["target"])
        return [n["id"] for n in self.nodes if n["id"] not in connected]
