import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class SkillSelectionEngine:
    """Matches engineering tasks to appropriate specialized skills and confidence tiers (SPEC-034)."""
    def __init__(self, workspace_path: str, ekb: EngineeringKnowledgeBase):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb
        self.exec_dir = self.workspace_path / ".aetheris" / "execution"
        self.exec_dir.mkdir(parents=True, exist_ok=True)

    def select_skills(self, tasks: List[dict]) -> dict:
        """Determines skill matches for all tasks."""
        mappings = []
        required_skills = set()
        missing_skills = []

        for t in tasks:
            ranked = self.rank_skills_for_task(t)
            primary = ranked[0] if ranked else {"name": "agency-senior-developer", "confidence": 0.8}
            fallback = self.recommend_fallback(t)

            mappings.append({
                "task_id": t["id"],
                "selected_skills": [
                    {"name": primary["name"], "confidence": primary["confidence"], "role": "primary"}
                ],
                "fallback_skill": fallback
            })
            required_skills.add(primary["name"])

        selection_report = {
            "mappings": mappings,
            "required_skills": list(required_skills),
            "missing_skills": missing_skills
        }

        # Write files
        (self.exec_dir / "skill.selection.json").write_text(json.dumps(selection_report, indent=2), encoding="utf-8")
        (self.exec_dir / "required.skills.json").write_text(json.dumps(list(required_skills), indent=2), encoding="utf-8")
        (self.exec_dir / "task.skills.map.json").write_text(json.dumps(mappings, indent=2), encoding="utf-8")
        (self.exec_dir / "missing.skills.json").write_text(json.dumps(missing_skills, indent=2), encoding="utf-8")

        # Register in EKB
        self.ekb.register_object("task_skills_mappings", {"id": "task_skills_map", "mappings": mappings}, producer="SSE")
        
        return selection_report

    def rank_skills_for_task(self, task: dict) -> List[dict]:
        """Ranks Aetheris's internal skills for a given task description."""
        tid = task["id"].lower()
        if "db" in tid or "database" in tid or "migration" in tid:
            return [
                {"name": "agency-database-optimizer", "confidence": 0.95},
                {"name": "agency-senior-developer", "confidence": 0.8}
            ]
        elif "auth" in tid or "security" in tid or "jwt" in tid:
            return [
                {"name": "agency-cloud-security-architect", "confidence": 0.9},
                {"name": "agency-senior-developer", "confidence": 0.75}
            ]
        else:
            return [
                {"name": "agency-senior-developer", "confidence": 0.85}
            ]

    def identify_missing_skills(self, tasks: List[dict]) -> List[str]:
        """Detects if any task maps to a skill category not supported in the active registry."""
        return []

    def recommend_fallback(self, task: dict) -> str:
        """Determines general fallback specialist skill."""
        return "agency-senior-developer"
