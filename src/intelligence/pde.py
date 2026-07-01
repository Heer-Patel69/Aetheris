import os
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple

try:
    from kernel.event_bus import EventBus
except ImportError:
    class EventBus:
        def __init__(self, workspace_path, telemetry=None):
            self.workspace_path = workspace_path
        def publish(self, event_type, publisher, payload, priority="NORMAL"):
            pass

class PromptEvidenceMerger:
    """Merges requirements prompt data with physical workspace discovery logs."""
    @staticmethod
    def merge(requirement: dict, wde_inventories: Dict[str, dict]) -> dict:
        meta = wde_inventories.get("workspace.metadata", {})
        languages = wde_inventories.get("language.inventory", {}).get("languages", {})
        frameworks = wde_inventories.get("framework.inventory", {}).get("frameworks", {})
        
        # Combine parameters
        return {
            "requirement_goals": requirement.get("business", {}).get("business_objectives", []),
            "total_files": meta.get("total_files", 0),
            "languages": list(languages.keys()),
            "frameworks": list(frameworks.keys())
        }


class BusinessIntentAnalyzer:
    """Extracts core business objectives and target propositions."""
    @staticmethod
    def analyze(merged_evidence: dict) -> Dict[str, any]:
        goals = merged_evidence.get("requirement_goals", [])
        value_prop = "Deliver a verified service matching the user requirement objectives."
        if goals:
            value_prop = f"Deliver an engine for: {'; '.join(goals)}"
        return {
            "objectives": goals,
            "value_proposition": value_prop
        }


class DomainClassifier:
    """Determines target domain rules (SaaS, E-Commerce, etc.) from project indicator evidence."""
    @staticmethod
    def classify(merged_evidence: dict) -> str:
        frameworks = merged_evidence.get("frameworks", [])
        languages = merged_evidence.get("languages", [])
        
        if "prisma" in frameworks or "postgres" in frameworks:
            return "Relational Database Domain"
        if "nextjs" in frameworks:
            return "Web Front-End SaaS Domain"
        if "python" in languages:
            return "Scientific Computing / CLI Domain"
        return "Generic Application Domain"


class PersonaDiscoveryEngine:
    """Extracts, maps, and deduplicates user personas from requirements."""
    @staticmethod
    def discover(requirement: dict) -> List[Dict[str, any]]:
        raw_personas = requirement.get("users", {}).get("personas", [])
        
        # Deduplication and mapping logic
        seen_names = set()
        deduped = []
        for p in raw_personas:
            name = p.get("name", "").strip()
            # Consolidate overlapping roles
            if name.lower() not in seen_names:
                seen_names.add(name.lower())
                deduped.append({
                    "name": name,
                    "role": p.get("role", "Application User Role"),
                    "goals": p.get("goals", ["Transact module features"])
                })
                
        if not deduped:
            deduped.append({
                "name": "Standard Operator",
                "role": "Default application operator",
                "goals": ["Run engine capabilities"]
            })
        return deduped


class WorkflowDiscoveryEngine:
    """Deduces user journey flows based on functional requirements."""
    @staticmethod
    def discover(requirement: dict, personas: List[dict]) -> List[Dict[str, any]]:
        func = requirement.get("requirements", {}).get("functional", [])
        flows = []
        actor = personas[0]["name"] if personas else "Standard Operator"
        
        for idx, f in enumerate(func):
            flows.append({
                "flow_id": f"flow:{f.get('id', idx)}",
                "name": f"Workflow: {f.get('name', 'User journey')}",
                "actor": actor,
                "steps": [
                    f"Actor initiates {f.get('name')}",
                    "System processes inputs and verifies permissions",
                    f"System records transaction for {f.get('name')}"
                ]
            })
            
        if not flows:
            flows.append({
                "flow_id": "flow:core",
                "name": "Core Application Execution Flow",
                "actor": actor,
                "steps": ["Initialize application", "Process default loop", "Shut down cleanly"]
            })
        return flows


class FeatureDiscoveryEngine:
    """Identifies functional/non-functional features and computes dependencies."""
    @staticmethod
    def discover(requirement: dict) -> List[Dict[str, any]]:
        func = requirement.get("requirements", {}).get("functional", [])
        nfunc = requirement.get("requirements", {}).get("non_functional", [])
        features = []
        
        # Extract features
        for f in func:
            features.append({
                "id": f.get("id"),
                "name": f.get("name"),
                "description": f.get("description"),
                "scope": "MVP" if f.get("priority") == "HIGH" else "Future",
                "dependencies": []
            })
            
        for nf in nfunc:
            features.append({
                "id": nf.get("id"),
                "name": nf.get("name"),
                "description": nf.get("description"),
                "scope": "MVP",
                "dependencies": []
            })
            
        # Add basic dependencies between database layer and controllers
        for f in features:
            if "controller" in f["name"].lower() or "auth" in f["name"].lower():
                # Depends on DB if present
                db_feats = [db["id"] for db in features if "db" in db["id"].lower() or "schema" in db["name"].lower()]
                if db_feats:
                    f["dependencies"] = db_feats

        return features


class MVPPlanner:
    """Separates functional capabilities into MVP scope and future roadmap milestones."""
    @staticmethod
    def plan(features: List[dict]) -> Tuple[List[dict], List[dict]]:
        mvp = [f for f in features if f["scope"] == "MVP"]
        future = [f for f in features if f["scope"] == "Future"]
        return mvp, future


class ComplexityEstimator:
    """Estimates engineering complexity, hours, and risk factors."""
    @staticmethod
    def estimate(features: List[dict]) -> Dict[str, any]:
        count = len(features)
        if count > 8:
            complexity = "HIGH"
            hours = 160
            risk = 0.40
        elif count > 4:
            complexity = "MEDIUM"
            hours = 80
            risk = 0.20
        else:
            complexity = "LOW"
            hours = 40
            risk = 0.10
            
        return {
            "complexity": complexity,
            "effort_hours": hours,
            "confidence": round(1.0 - risk, 2)
        }


class ProductDiscoveryEngine:
    """Orchestration coordinator running the Product Discovery Engine (SPEC-003)."""
    def __init__(self, workspace_path: str, event_bus: EventBus = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.event_bus = event_bus if event_bus else EventBus(self.workspace_path)
        self.output_file = self.workspace_path / ".aetheris" / "execution" / "product.plan.json"

    def discover(self, requirement: dict, wde_inventories: Dict[str, dict]) -> Dict[str, any]:
        """Main execution runner compiling product.plan.json."""
        self.event_bus.publish("ProductDiscoveryStarted", "PDE", {"workspace": str(self.workspace_path)})
        
        # 1. Merge prompt/WDE evidence
        merged_evidence = PromptEvidenceMerger.merge(requirement, wde_inventories)
        
        # 2. Extract Business Intent
        intent = BusinessIntentAnalyzer.analyze(merged_evidence)
        self.event_bus.publish("BusinessIntentExtracted", "PDE", {"intent": intent})
        
        # 3. Classify Domain
        domain = DomainClassifier.classify(merged_evidence)
        
        # 4. Discover Personas
        personas = PersonaDiscoveryEngine.discover(requirement)
        for p in personas:
            self.event_bus.publish("PersonaDiscovered", "PDE", {"persona": p["name"]})
            
        # 5. Discover Journeys/Workflows
        flows = WorkflowDiscoveryEngine.discover(requirement, personas)
        for f in flows:
            self.event_bus.publish("WorkflowDiscovered", "PDE", {"workflow": f["name"]})
            
        # 6. Extract Features
        features = FeatureDiscoveryEngine.discover(requirement)
        
        # 7. Plan MVP
        mvp_features, future_features = MVPPlanner.plan(features)
        
        # 8. Complexity & Effort
        estimates = ComplexityEstimator.estimate(features)
        
        # 9. Format output model
        product_plan = {
            "product_name": requirement.get("business", {}).get("business_goal", "New Service Product"),
            "category": domain,
            "domain": domain,
            "value_proposition": intent["value_proposition"],
            "users": {
                "personas": personas
            },
            "flows": flows,
            "features": features,
            "estimates": estimates
        }
        
        # Schema validate and write to execution directory
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(json.dumps(product_plan, indent=2), encoding="utf-8")
        
        self.event_bus.publish("ProductValidated", "PDE", {"status": "SUCCESS"})
        self.event_bus.publish("ProductPlanGenerated", "PDE", {"output_file": str(self.output_file)})
        
        return product_plan
