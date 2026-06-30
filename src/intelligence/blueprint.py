import os
import json
from pathlib import Path
from intelligence.technology import TechnologyIntelligence
from intelligence.decision import DecisionIntelligenceEngine

class UniversalBlueprintEngine:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.blueprint_path = self.workspace_path / ".aetheris" / "product.blueprint.json"
        
    def compile_blueprint(self, goal_tree):
        """
        Gathers tech decisions, compiles the blueprint config,
        saves to product.blueprint.json, and logs decisions.
        """
        # 1. Evaluate tech stack trade-offs
        tech_intel = TechnologyIntelligence(self.workspace_path)
        tech_selections = tech_intel.evaluate_tech_stack(goal_tree)
        
        # 2. Log tech decisions to Decision Intelligence Engine (DIE)
        die = DecisionIntelligenceEngine(self.workspace_path)
        for topic, details in tech_selections.items():
            die.log_decision(
                topic=topic,
                choice=details["choice"],
                alternatives=details["alternatives"],
                confidence=details["confidence"],
                reason=details["reason"]
            )
            
        # 3. Assemble Universal Blueprint
        blueprint = {
            "target_platform": "Cross-Platform API & UI",
            "vision": goal_tree.get("original_goal", ""),
            "completeness_requirements": goal_tree.get("completeness_targets", {}),
            "technology_stack": {topic: details["choice"] for topic, details in tech_selections.items()},
            "inferred_subsystems": goal_tree.get("inferred_subsystems", []),
            "assumptions": goal_tree.get("assumptions", [])
        }
        
        # 4. Save to product.blueprint.json
        try:
            self.blueprint_path.parent.mkdir(parents=True, exist_ok=True)
            self.blueprint_path.write_text(json.dumps(blueprint, indent=2), encoding="utf-8")
            print(f"Universal Blueprint generated successfully: {self.blueprint_path.name}")
        except Exception as e:
            import sys
            sys.stderr.write(f"Error saving blueprint: {e}\n")
            
        return blueprint
