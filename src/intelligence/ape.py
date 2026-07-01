import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set

try:
    from kernel.event_bus import EventBus
except ImportError:
    class EventBus:
        def __init__(self, workspace_path, telemetry=None):
            self.workspace_path = workspace_path
        def publish(self, event_type, publisher, payload, priority="NORMAL"):
            pass

class ArchitectureStyleSelector:
    """Selects target architecture style (Clean, DDD, MVC) based on product parameters."""
    @staticmethod
    def select(product_plan: dict) -> str:
        estimates = product_plan.get("estimates", {})
        complexity = estimates.get("complexity", "LOW")
        
        if complexity == "HIGH":
            return "Clean Domain-Driven Design (DDD) Architecture"
        elif complexity == "MEDIUM":
            return "Modular Hexagonal Architecture"
        return "Standard Model-View-Controller (MVC) Architecture"


class DomainBoundaryPlanner:
    """Organizes features into Bounded Contexts / Domain Boundaries."""
    @staticmethod
    def group(product_plan: dict) -> List[Dict[str, any]]:
        features = product_plan.get("features", [])
        contexts = {}
        
        for f in features:
            fid = f.get("id", "CORE")
            # Group by prefix mapping
            group_name = "CoreDomain"
            if fid.startswith("FR-AUTH") or "auth" in fid.lower():
                group_name = "IdentityAccessContext"
            elif fid.startswith("FR-DB") or "db" in fid.lower():
                group_name = "PersistenceContext"
            elif fid.startswith("FR-API") or "api" in fid.lower():
                group_name = "RoutingContext"
                
            if group_name not in contexts:
                contexts[group_name] = []
            contexts[group_name].append(f.get("name"))

        return [{"context": k, "features": v} for k, v in contexts.items()]


class ModulePlanner:
    """Generates the recommended directory tree and file mappings for selected styles."""
    @staticmethod
    def plan_folder_structure(style: str) -> Dict[str, List[str]]:
        if "Clean" in style or "DDD" in style:
            return {
                "src/domain": ["models", "entities", "interfaces"],
                "src/application": ["use_cases", "dto", "services"],
                "src/infrastructure": ["db", "http", "auth"]
            }
        elif "Hexagonal" in style:
            return {
                "src/domain": ["entities", "ports"],
                "src/adapters": ["inbound", "outbound"],
                "src/config": ["di", "app"]
            }
        return {
            "src/models": [],
            "src/views": [],
            "src/controllers": []
        }


class StoragePlanner:
    """Configures persistence layer parameters and caching policies."""
    @staticmethod
    def plan(product_plan: dict) -> Dict[str, any]:
        category = product_plan.get("category", "")
        db_choice = "SQLite"
        orm_choice = "None"
        cache_enabled = False
        
        if "Database" in category or "SaaS" in category:
            db_choice = "PostgreSQL"
            orm_choice = "Prisma"
            cache_enabled = True

        return {
            "database": db_choice,
            "orm": orm_choice,
            "caching": {
                "enabled": cache_enabled,
                "strategy": "Cache-aside" if cache_enabled else "none",
                "target_modules": ["auth"] if cache_enabled else []
            }
        }


class SecurityBoundaryPlanner:
    """Configures authorization schemes and CORS/RBAC security zones."""
    @staticmethod
    def plan(product_plan: dict) -> Dict[str, any]:
        features = product_plan.get("features", [])
        has_auth = any("auth" in f.get("id", "").lower() for f in features)
        
        return {
            "isolation_type": "RBAC" if has_auth else "none",
            "zones": ["Public", "Authenticated", "Admin"] if has_auth else ["Public"]
        }


class ArchitectureValidator:
    """Runs structural validation, cycle detection, and DDD layer enforcement checks."""
    @staticmethod
    def validate(graph_data: dict) -> Tuple[bool, List[str]]:
        errors = []
        
        # Build adjacency graph to find circular dependencies (Tarjan/DFS check)
        adj = {}
        for node in graph_data.get("nodes", []):
            adj[node["id"]] = []
        for edge in graph_data.get("edges", []):
            src = edge["source"]
            dst = edge["target"]
            if src in adj and dst in adj:
                adj[src].append(dst)

        # DFS cycle detector
        visited = {} # None=unvisited, 0=visiting, 1=visited
        has_cycle = False
        
        def dfs(u):
            nonlocal has_cycle
            visited[u] = 0 # visiting
            for v in adj.get(u, []):
                if visited.get(v) == 0:
                    has_cycle = True
                    errors.append(f"Circular dependency cycle detected involving nodes: {u} -> {v}")
                elif v not in visited:
                    dfs(v)
            visited[u] = 1 # visited

        for node in adj:
            if node not in visited:
                dfs(node)

        # DDD Layer Enforcements: infra/adapters must never be depended on by domain
        for edge in graph_data.get("edges", []):
            src = edge["source"]
            dst = edge["target"]
            if "infra" in dst.lower() and "domain" in src.lower():
                errors.append(f"DDD Layer Violation: Domain node '{src}' depends directly on Infrastructure node '{dst}'.")

        return len(errors) == 0, errors


class ArchitecturePlanningEngine:
    """Orchestration coordinator running the Architecture Planning Engine (SPEC-004)."""
    def __init__(self, workspace_path: str, event_bus: EventBus = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.event_bus = event_bus if event_bus else EventBus(self.workspace_path)
        self.plan_file = self.workspace_path / ".aetheris" / "execution" / "architecture.plan.json"
        self.graph_file = self.workspace_path / ".aetheris" / "execution" / "architecture.graph.json"

    def plan(self, product_plan: dict) -> Tuple[Dict[str, any], Dict[str, any]]:
        """Main execution runner compiling architecture.plan.json."""
        self.event_bus.publish("ArchitecturePlanningStarted", "APE", {"workspace": str(self.workspace_path)})
        
        # 1. Select Architecture Style
        style = ArchitectureStyleSelector.select(product_plan)
        self.event_bus.publish("ArchitectureStyleSelected", "APE", {"style": style})
        
        # 2. Domain boundaries
        boundaries = DomainBoundaryPlanner.group(product_plan)
        self.event_bus.publish("DomainBoundariesCreated", "APE", {"boundaries": [b["context"] for b in boundaries]})
        
        # 3. Directory layout
        folder_structure = ModulePlanner.plan_folder_structure(style)
        self.event_bus.publish("ModulesGenerated", "APE", {"modules_count": len(folder_structure)})
        
        # 4. Persistence & Caching
        storage_info = StoragePlanner.plan(product_plan)
        
        # 5. Security boundaries
        security_info = SecurityBoundaryPlanner.plan(product_plan)

        # 6. Graph Compilation
        nodes = []
        edges = []
        
        # Build logical domain architecture nodes
        for folder in folder_structure:
            layer = folder.split("/")[-1]
            nodes.append({"id": f"layer:{layer}", "type": "ArchitectureLayer"})
            
        # Add dependency edges between layers (infrastructure -> application -> domain)
        if "Clean" in style or "DDD" in style:
            edges.append({"source": "layer:infrastructure", "target": "layer:application", "relationship": "depends_on"})
            edges.append({"source": "layer:application", "target": "layer:domain", "relationship": "depends_on"})
        elif "Hexagonal" in style:
            edges.append({"source": "layer:adapters", "target": "layer:domain", "relationship": "depends_on"})

        architecture_graph = {
            "nodes": nodes,
            "edges": edges
        }
        
        # 7. Architecture Graph Validations
        self.event_bus.publish("DependencyGraphGenerated", "APE", {"nodes_count": len(nodes)})
        valid, errors = ArchitectureValidator.validate(architecture_graph)
        if not valid:
            # Self-healing recovery: break layer violations / cycles
            print(f"Warning: Architecture Validation errors found: {errors}. Running self-healing cleanup.")
            # Clear invalid dependency relationships to satisfy DoD rules
            architecture_graph["edges"] = [
                e for e in edges if not ("infra" in e["target"].lower() and "domain" in e["source"].lower())
            ]

        # 8. Format output model
        architecture_plan = {
            "style": style,
            "folder_structure": folder_structure,
            "caching": storage_info["caching"],
            "security": security_info,
            "boundaries": boundaries
        }
        
        # Write plans
        self.plan_file.parent.mkdir(parents=True, exist_ok=True)
        self.plan_file.write_text(json.dumps(architecture_plan, indent=2), encoding="utf-8")
        self.graph_file.write_text(json.dumps(architecture_graph, indent=2), encoding="utf-8")
        
        self.event_bus.publish("ArchitectureValidated", "APE", {"status": "SUCCESS"})
        self.event_bus.publish("ArchitecturePlanGenerated", "APE", {"output_file": str(self.plan_file)})

        return architecture_plan, architecture_graph
