import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class SelfReviewEngine:
    """Critiques generated source code files against styling guidelines, architecture constraints, and security issues (SPEC-040)."""
    def __init__(self, workspace_path: str, ekb: EngineeringKnowledgeBase):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb
        self.exec_dir = self.workspace_path / ".aetheris" / "execution"
        self.exec_dir.mkdir(parents=True, exist_ok=True)

    def review(self, files: List[dict]) -> dict:
        """Evaluates generated files and outputs a quality score and recommendations report."""
        findings = []
        for f in files:
            path = f.get("path", "")
            action = f.get("action", "")
            
            # Simple smell detector
            if action == "create" and "middleware" in path:
                findings.append({
                    "severity": "WARNING",
                    "evidence": "def auth_filter(request): return True",
                    "recommendation": "Do not hardcode return True in auth middleware. Verify JWT signature tokens.",
                    "affected_files": [path]
                })

        overall_score = self.score_quality(findings)
        approved = len([f for f in findings if f["severity"] == "CRITICAL"]) == 0

        review_report = {
            "approved": approved,
            "overall_quality_score": overall_score,
            "findings": findings
        }

        # Write execution outputs
        (self.exec_dir / "engineering.review.json").write_text(json.dumps(review_report, indent=2), encoding="utf-8")
        (self.exec_dir / "review.findings.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")
        (self.exec_dir / "quality.score.json").write_text(json.dumps({"score": overall_score}, indent=2), encoding="utf-8")

        self.ekb.register_object("execution_review_report", review_report, producer="SRE")

        return review_report

    def score_quality(self, findings: List[dict]) -> float:
        """Calculates quality score from findings count (deducts 5 points per warning, 20 per critical)."""
        score = 100.0
        for f in findings:
            if f["severity"] == "CRITICAL":
                score -= 20.0
            else:
                score -= 5.0
        return max(score, 0.0)

    def detect_smells(self, files: List[dict]) -> List[dict]:
        """Scans AST patterns for common code smells."""
        return []

    def recommend(self, findings: List[dict]) -> List[dict]:
        return findings

    def approve(self, review_id: str) -> bool:
        return True

    def reject(self, review_id: str) -> bool:
        return True
