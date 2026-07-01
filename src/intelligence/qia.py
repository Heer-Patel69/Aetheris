import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase
from intelligence.ege import EngineeringGraphEngine

class QueryParser:
    """Parses text query inputs to extract main target names and subject tokens."""
    @staticmethod
    def parse(query_text: str) -> dict:
        text = query_text.lower().strip()
        target = "unknown"
        
        # Simple extraction rules
        if "breaks if" in text:
            parts = text.split("breaks if")
            if len(parts) > 1:
                target = parts[1].replace("changes", "").replace("?", "").strip()
        elif "depend on" in text:
            parts = text.split("depend on")
            if len(parts) > 1:
                target = parts[1].replace("?", "").strip()
        elif "implement" in text:
            parts = text.split("implement")
            if len(parts) > 1:
                target = parts[1].replace("?", "").strip()
                
        # Normalize target naming conventions
        if target.startswith("database") or target == "db":
            target = "layer:infrastructure"
        elif target.startswith("auth") or target == "authentication":
            target = "layer:application"

        return {
            "query_raw": query_text,
            "target": target
        }


class IntentResolver:
    """Classifies queries into LOOKUP, DEPENDENCY, IMPACT, or SECURITY intents."""
    @staticmethod
    def resolve(query_text: str) -> str:
        text = query_text.lower()
        if "breaks if" in text or "impact of" in text:
            return "IMPACT"
        if "depend on" in text or "dependencies" in text:
            return "DEPENDENCY"
        if "secure" in text or "auth" in text or "role" in text:
            return "SECURITY"
        return "LOOKUP"


class GraphTraversalEngine:
    """Traverses EGE graph nodes to find direct or transitive connections."""
    def __init__(self, ege: EngineeringGraphEngine):
        self.ege = ege

    def get_dependents(self, node_id: str) -> List[str]:
        """BFS walk to find all nodes that depend directly or transitively on node_id."""
        incoming = {n["id"]: [] for n in self.ege.nodes}
        for e in self.ege.edges:
            src = e["source"]
            dst = e["target"]
            if src in incoming and dst in incoming:
                incoming[dst].append(src)

        if node_id not in incoming:
            return []

        visited = {node_id}
        queue = [node_id]
        dependents = []

        while queue:
            curr = queue.pop(0)
            for neighbor in incoming.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    dependents.append(neighbor)
        return dependents


class ImpactAnalyzer:
    """Compiles cascading change-impact reports based on graph traversals."""
    @staticmethod
    def compile_report(target_node: str, dependents: List[str]) -> dict:
        affected = []
        for d in dependents:
            # Simple path distance simulation for report schema
            affected.append({
                "id": d,
                "type": "ArchitectureLayer" if d.startswith("layer:") else "Task",
                "path_distance": 1
            })
            
        risks = []
        if len(affected) > 2:
            risks.append("Cascading changes may impact multiple core layers. Comprehensive regression tests required.")
        elif affected:
            risks.append("Low risk: local scope dependents affected.")
        else:
            risks.append("No active dependents found in dependency graph.")

        return {
            "target_node": target_node,
            "total_affected": len(affected),
            "affected_nodes": affected,
            "risks": risks
        }


class QueryAndImpactAnalysisEngine:
    """Universal reasoning gateway for all subsystems (SPEC-008)."""
    def __init__(self, workspace_path: str, ekb: Optional[EngineeringKnowledgeBase] = None, ege: Optional[EngineeringGraphEngine] = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb if ekb else EngineeringKnowledgeBase(str(self.workspace_path))
        self.ege = ege if ege else EngineeringGraphEngine(str(self.workspace_path))
        
        self.query_index_file = self.workspace_path / ".aetheris" / "execution" / "query.index.json"
        self.impact_index_file = self.workspace_path / ".aetheris" / "execution" / "impact.index.json"

    def query(self, query_text: str) -> dict:
        """Determines intent, traverses EGE graph, and returns explanation."""
        parsed = QueryParser.parse(query_text)
        intent = IntentResolver.resolve(query_text)
        target = parsed["target"]

        summary = f"Query executed successfully under {intent} context."
        evidence = []
        targets = []
        confidence = 0.50

        # Retrieve matching metadata or run traversals
        if intent == "IMPACT":
            traverser = GraphTraversalEngine(self.ege)
            dependents = traverser.get_dependents(target)
            report = ImpactAnalyzer.compile_report(target, dependents)
            summary = f"Changing '{target}' affects {report['total_affected']} components."
            targets = dependents
            evidence = report["risks"]
            confidence = 0.90
        elif intent == "DEPENDENCY":
            edges = [e for e in self.ege.edges if e["source"] == target]
            targets = [e["target"] for e in edges]
            summary = f"Node '{target}' depends directly on {len(targets)} components."
            evidence = [f"Found edge reference in EGE graph: {target} -> {t}" for t in targets]
            confidence = 0.85
        else:
            # General Lookup
            objs = self.ekb.query_objects({"type": "decision"})
            targets = [o["content"]["selected_option"] for o in objs]
            summary = f"Located {len(targets)} active technology selections in Knowledge Base."
            evidence = [f"EKB record ID: {o['object_id']}" for o in objs]
            confidence = 0.95

        result = {
            "query": query_text,
            "intent": intent,
            "answer": {
                "summary": summary,
                "targets": targets,
                "evidence": evidence
            },
            "confidence": confidence
        }

        # Write to execution indexes
        try:
            self.query_index_file.parent.mkdir(parents=True, exist_ok=True)
            self.query_index_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        except Exception:
            pass

        return result

    def analyze_impact(self, node_id: str) -> dict:
        """Runs the BFS impact traversal and writes the impact.index.json file."""
        traverser = GraphTraversalEngine(self.ege)
        dependents = traverser.get_dependents(node_id)
        report = ImpactAnalyzer.compile_report(node_id, dependents)

        try:
            self.impact_index_file.parent.mkdir(parents=True, exist_ok=True)
            self.impact_index_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        except Exception:
            pass

        return report
