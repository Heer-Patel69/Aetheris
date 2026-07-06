import re
from pathlib import Path
from typing import Dict, Any, List

class PolicyEngine:
    """
    AEKS v1.0 Policy Engine.
    Validates generated artifacts against coding, security, and architecture rules.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_root = Path(workspace_path).resolve()
        
    def validate_artifact(self, filename: str, content: str) -> Dict[str, Any]:
        """Validates artifact content against policies."""
        violations = []
        
        # 1. Security Check: Prevent hardcoded secret patterns
        secret_patterns = [
            r"(?i)password\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)secret_key\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)api_key\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)token\s*=\s*['\"][^'\"]+['\"]"
        ]
        for pat in secret_patterns:
            if re.search(pat, content):
                violations.append({
                    "severity": "CRITICAL",
                    "rule": "No Hardcoded Secrets",
                    "message": "Potential hardcoded credentials/secrets found in artifact."
                })
                
        # 2. Architecture Check: Layer import rules (e.g. domain layers must not import infrastructure layers)
        if filename.endswith(".py") and "domain" in filename:
            if "import infrastructure" in content or "from infrastructure" in content:
                violations.append({
                    "severity": "HIGH",
                    "rule": "Clean Layer Architecture",
                    "message": "Domain layer violates dependency inversion by directly importing infrastructure."
                })
                
        # 3. Accessibility / Web standard rules (for UI templates)
        if filename.endswith((".html", ".tsx", ".js")):
            if "<img" in content and "alt=" not in content:
                violations.append({
                    "severity": "MEDIUM",
                    "rule": "Accessibility Alt Tag",
                    "message": "Image element lacks alternate description (alt text)."
                })

        return {
            "success": len(violations) == 0,
            "violations": violations
        }
