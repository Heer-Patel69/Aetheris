import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class EngineeringDecisionEngine:
    """Authoritative decision governor selecting and versioning tech stack choices (SPEC-005)."""
    def __init__(self, workspace_path: str, ekb: Optional[EngineeringKnowledgeBase] = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb if ekb else EngineeringKnowledgeBase(str(self.workspace_path))
        
        # Technology database matching scores: Performance, Cost, Maintainability, Evidence
        self.registry = {
            "database": {
                "PostgreSQL": {"perf": 0.90, "cost": 0.70, "maint": 0.85, "evidence": 1.0},
                "SQLite": {"perf": 0.80, "cost": 1.00, "maint": 0.95, "evidence": 1.0},
                "MySQL": {"perf": 0.85, "cost": 0.80, "maint": 0.80, "evidence": 1.0}
            },
            "caching": {
                "Redis": {"perf": 0.98, "cost": 0.60, "maint": 0.80, "evidence": 1.0},
                "InMemory": {"perf": 0.95, "cost": 1.00, "maint": 0.95, "evidence": 1.0}
            },
            "auth": {
                "JWT": {"perf": 0.90, "cost": 1.00, "maint": 0.90, "evidence": 1.0},
                "OAuth2": {"perf": 0.85, "cost": 0.80, "maint": 0.75, "evidence": 1.0}
            }
        }

    def evaluate_decision(self, category: str, alternatives: List[str], weights: Optional[dict] = None) -> dict:
        """Determines the highest scoring engineering option and logs the decision in EKB."""
        w = weights or {"perf": 0.3, "cost": 0.3, "maint": 0.2, "evidence": 0.2}
        cat_registry = self.registry.get(category, {})
        
        best_option = None
        best_score = -1.0
        
        for opt in alternatives:
            metrics = cat_registry.get(opt, {"perf": 0.5, "cost": 0.5, "maint": 0.5, "evidence": 0.5})
            score = (
                w["perf"] * metrics["perf"] +
                w["cost"] * metrics["cost"] +
                w["maint"] * metrics["maint"] +
                w["evidence"] * metrics["evidence"]
            )
            if score > best_score:
                best_score = score
                best_option = opt

        decision_id = f"dec_{category}"
        decision_content = {
            "id": decision_id,
            "category": category,
            "selected_option": best_option,
            "alternatives": alternatives,
            "tradeoffs": {
                "benefits": [f"Optimized score of {round(best_score, 2)} chosen for {best_option}"],
                "drawbacks": [f"Alternatives {list(set(alternatives) - {best_option})} bypassed"]
            },
            "confidence_score": round(best_score, 2),
            "rationale": f"Authoritative selection based on EDE multi-criteria scoring algorithm."
        }

        # Save to Knowledge Base
        self.ekb.register_object("decision", decision_content, producer="EDE")
        
        # Save compatibility file
        compat_file = self.workspace_path / ".aetheris" / "execution" / f"{decision_id}.json"
        compat_file.parent.mkdir(parents=True, exist_ok=True)
        compat_file.write_text(json.dumps(decision_content, indent=2), encoding="utf-8")

        return decision_content

    def rollback_decision(self, category: str, target_version: int) -> Optional[dict]:
        """Restores a previous version of a registered decision in EKB."""
        decision_id = f"dec_{category}"
        history_file = self.ekb.kb_dir / f"{decision_id}_history.json"
        if not history_file.exists():
            return None
            
        ver_obj = self.ekb.get_object(decision_id, version=target_version)
        if not ver_obj:
            return None
            
        # Re-register content under a new increment version
        restored_content = ver_obj["content"]
        self.ekb.register_object("decision", restored_content, producer="EDE_Rollback")
        
        return restored_content
