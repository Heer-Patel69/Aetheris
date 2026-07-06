import os
import sys
import json
import unittest
from pathlib import Path

# Add src to python path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from aetheris.adapters.template_adapter import TemplateAdapter
from aetheris.adapters.agent_runtime import AgentRuntimeOrchestrator
from aetheris.adapters.proxy_adapter import ProxyAdapter

class TestAdapters(unittest.TestCase):
    def setUp(self):
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.manifest_path = self.workspace_root / ".aetheris" / "ENGINEERING_MANIFEST.json"
        
        # Ensure a mock manifest exists for tests
        if not self.manifest_path.parent.exists():
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.test_manifest = {
            "current_phase": "Phase 6: Backend Routing",
            "task_id": "test-task-123",
            "rules": ["Be concise", "No placeholders"]
        }
        self.manifest_path.write_text(json.dumps(self.test_manifest, indent=2), encoding="utf-8")

    def tearDown(self):
        # Clean up mock manifest
        if self.manifest_path.exists():
            self.manifest_path.unlink()

    def test_theme_contract_validity(self):
        """Verify the monochromatic minimal luxury theme config exists and is valid JSON."""
        theme_path = self.workspace_root / "src" / "config" / "theme_contract.json"
        self.assertTrue(theme_path.exists())
        theme_data = json.loads(theme_path.read_text(encoding="utf-8"))
        self.assertEqual(theme_data["theme"]["name"], "Monochromatic Minimal Luxury")
        self.assertIn("colors", theme_data["theme"])
        self.assertIn("bg-core", theme_data["theme"]["colors"])
        self.assertIn("brand-accent", theme_data["theme"]["colors"])

    def test_template_adapter_sync(self):
        """Verify TemplateAdapter sync functionality, outputting skills and RFCs."""
        adapter = TemplateAdapter(str(self.workspace_root))
        res = adapter.sync()
        
        # Verify sync executed without failing
        self.assertIn("skills_copied", res)
        self.assertIn("rfcs_copied", res)
        self.assertEqual(len(res["errors"]), 0)
        
        # Ensure target files exist
        skills_dir = self.workspace_root / "skills" / "third_party" / "claude_templates"
        self.assertTrue(skills_dir.exists())
        
        accessibility_skill = skills_dir / "accessibility.md"
        self.assertTrue(accessibility_skill.exists())
        
        # Verify frontmatter conversion
        skill_content = accessibility_skill.read_text(encoding="utf-8")
        self.assertTrue(skill_content.startswith("---"))
        self.assertIn("color: slate", skill_content)
        self.assertTrue(any(e in skill_content for e in ["emoji: \"\\U0001F916\"", "emoji: \"\\U0001f916\"", "emoji: 🤖"]))

        # Verify global rules copies
        rfcs_dir = self.workspace_root / "rfcs" / "third_party"
        self.assertTrue(rfcs_dir.exists())
        self.assertTrue((rfcs_dir / "CLAUDE.md").exists())
        self.assertTrue((rfcs_dir / "AGENTS.md").exists())
        self.assertTrue((rfcs_dir / "RULES.md").exists())

    def test_agent_runtime_manifest_injection(self):
        """Verify AgentRuntimeOrchestrator correctly loads and maps manifest values to environment variables."""
        orchestrator = AgentRuntimeOrchestrator(str(self.workspace_root))
        env = orchestrator.prepare_environment()
        
        self.assertEqual(env["AETHERIS_ACTIVE_PHASE"], "Phase 6: Backend Routing")
        self.assertEqual(env["AETHERIS_TASK_ID"], "test-task-123")
        self.assertIn("CLAUDE_CODE_STATELESS", env)
        self.assertEqual(env["CLAUDE_CODE_STATELESS"], "1")

        # Parse injected manifest JSON back
        manifest_back = json.loads(env["AETHERIS_MANIFEST_DATA"])
        self.assertEqual(manifest_back["current_phase"], "Phase 6: Backend Routing")
        self.assertEqual(manifest_back["task_id"], "test-task-123")

    def test_proxy_adapter_smart_crusher_rules(self):
        """Verify SmartCrusher compresses logs/JSON while preserving code blocks with 0% compression."""
        adapter = ProxyAdapter(str(self.workspace_root))
        
        # Test case 1: Source code block (should not be touched)
        source_code_input = "```python\n# This is source code\ndef hello():\n    print('Hello')\n```"
        self.assertEqual(adapter.apply_smart_crusher_rules(source_code_input), source_code_input)
        
        # Test case 2: Redundant logs (should be compressed)
        log_input = "```logs\n" + "\n".join([f"Log line {i}: Operation successful" for i in range(20)]) + "\n```"
        compressed_logs = adapter.apply_smart_crusher_rules(log_input)
        self.assertIn("Compressed 12 lines", compressed_logs)
        self.assertIn("Log line 0", compressed_logs)
        self.assertIn("Log line 19", compressed_logs)
        
        # Test case 3: Large JSON payload (should be compacted/shortened)
        json_input = "```json\n" + json.dumps({
            "items": [i for i in range(20)],
            "metadata": {"source": "telemetry"}
        }, indent=2) + "\n```"
        compressed_json = adapter.apply_smart_crusher_rules(json_input)
        # Verify JSON is compacted (no extra whitespaces)
        self.assertNotIn("  ", compressed_json)
        self.assertIn("Truncated", compressed_json)

if __name__ == "__main__":
    unittest.main()
