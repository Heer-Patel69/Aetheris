import os
import json
from pathlib import Path
from kernel.utils import is_safe_path, redact_secrets

class DecisionIntelligenceEngine:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.decision_log_path = self.workspace_path / ".aetheris" / "memory" / "tech-decisions.jsonl"
        
    def log_decision(self, topic, choice, alternatives, confidence, reason, evidence="", risk="", migration_path=""):
        """
        Appends an auditable technology decision record to tech-decisions.jsonl.
        """
        try:
            self.decision_log_path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "topic": topic,
                "choice": choice,
                "alternatives": alternatives,
                "confidence": confidence,
                "reason": reason,
                "evidence": evidence,
                "risk": risk,
                "migration_path": migration_path
            }
            
            line = json.dumps(record)
            scrubbed_line = redact_secrets(line)
            
            with open(self.decision_log_path, "a", encoding="utf-8") as f:
                f.write(scrubbed_line + "\n")
            
            print(f"Logged Tech Decision: [{topic}] -> {choice} (confidence={confidence*100}%)")
            return True
        except Exception as e:
            import sys
            sys.stderr.write(f"Error logging tech decision: {e}\n")
            return False
            
    def get_decisions(self):
        """
        Reads historical tech decisions.
        """
        if not self.decision_log_path.exists():
            return []
        decisions = []
        try:
            with open(self.decision_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        decisions.append(json.loads(line.strip()))
            return decisions
        except Exception:
            return []
