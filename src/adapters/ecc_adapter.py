"""
ECCAdapter — Production Implementation (Phase 3).

Translates ECC (Engineering Control Centre) Workflow Templates into:
  - Planning hooks
  - Engineering process definitions
  - Task acceptance criteria
  - Quality gate configurations
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base_adapter import IntegrationAdapter


class ECCAdapter(IntegrationAdapter):
    """
    ECC Workflow Template adapter.
    Reads templates from .aetheris/config/ecc_templates/ and translates
    them into runtime-executable planning structures.
    """

    DEFAULT_TEMPLATES = {
        "feature":      {"gates": ["compilation", "unit_tests", "lint"], "quality_threshold": 0.85},
        "bugfix":       {"gates": ["compilation", "unit_tests", "regression"], "quality_threshold": 0.90},
        "architecture": {"gates": ["compilation", "integration_tests", "security", "performance"], "quality_threshold": 0.95},
        "documentation":{"gates": ["spell_check", "link_check"], "quality_threshold": 0.80},
    }

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self._templates: Dict[str, Any] = {}
        self._hooks: List[Dict[str, Any]] = []

    def initialize(self):
        """Load ECC templates from disk or fall back to defaults."""
        template_dir = self.workspace_path / ".aetheris" / "config" / "ecc_templates"
        if template_dir.exists():
            for f in template_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    self._templates[f.stem] = data
                except Exception:
                    pass
        if not self._templates:
            self._templates = dict(self.DEFAULT_TEMPLATES)

    # ── translation API ───────────────────────────────────────────────────────

    def translate_template(self, template_name: str,
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Translate a named ECC template into an executable planning structure."""
        tmpl = self._templates.get(template_name, self._templates.get("feature", {}))
        ctx  = context or {}
        return {
            "template":           template_name,
            "quality_gates":      tmpl.get("gates", ["compilation"]),
            "quality_threshold":  tmpl.get("quality_threshold", 0.85),
            "acceptance_criteria": ctx.get("acceptance_criteria", []),
            "hooks":              self._hooks,
            "resolved_at":        __import__("time").time(),
        }

    def register_hook(self, hook: Dict[str, Any]):
        """Register an engineering process hook."""
        self._hooks.append(hook)

    def get_quality_gates(self, task_type: str) -> List[str]:
        """Return quality gates for a task type."""
        tmpl = self._templates.get(task_type, self._templates.get("feature", {}))
        return tmpl.get("gates", ["compilation", "unit_tests"])

    def list_templates(self) -> List[str]:
        return list(self._templates.keys())

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def start(self):
        self.initialize()

    def stop(self):
        pass
