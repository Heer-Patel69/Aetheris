import unittest
import shutil
import json
from pathlib import Path
from intelligence.urue import (
    UniversalRequirementUnderstandingEngine,
    PromptNormalizer,
    IntentExtractor,
    RequirementExpander
)

class TestURUE(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_urue_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        self.urue = UniversalRequirementUnderstandingEngine(str(self.workspace_path))
        
        # Mock WDE inventories input
        self.wde_inventories = {
            "workspace.inventory": {
                "workspace_root": str(self.workspace_path),
                "files": [
                    {"path": "schema.prisma", "size_bytes": 100, "modified_at": 0.0, "fingerprint": "hash"}
                ]
            },
            "filesystem.graph": {"nodes": [], "edges": []},
            "workspace.metadata": {"total_files": 1, "total_directories": 0, "git_branch": "main", "git_commit": "hash", "git_dirty": False},
            "language.inventory": {"languages": {"prisma": {"file_count": 1, "percentage": 1.0}}},
            "framework.inventory": {"frameworks": {"prisma": {"confidence": 1.0, "evidence": "exists"}}},
            "dependency.inventory": {"package_manager": "npm", "dependencies": {"prisma": "^5.0.0"}}
        }

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_prompt_normalizer(self):
        p = "  Test   raw   prompt  "
        self.assertEqual(PromptNormalizer.normalize(p), "Test raw prompt")
        self.assertEqual(PromptNormalizer.normalize(""), "autonomous execution")

    def test_intent_extractor(self):
        intent = IntentExtractor.extract("Build me a multi-tenant CRM SaaS app with secure login")
        self.assertEqual(intent["category"], "CRM Platform") # Matches 'crm' first in keywords order
        self.assertTrue(any("Secure user" in obj for obj in intent["business_objectives"]))

    def test_requirement_expander(self):
        expanded = RequirementExpander.expand(
            prompt_text="login authentication via REST api",
            category="SaaS Multi-tenant Platform",
            base_reqs={"functional": [], "non_functional": []}
        )
        # Should expand with multi-tenant isolation, API routes, and rate limits
        func_ids = {r["id"] for r in expanded["functional"]}
        nfunc_ids = {r["id"] for r in expanded["non_functional"]}
        
        self.assertIn("FR-TENANT", func_ids)
        self.assertIn("FR-API", func_ids)
        self.assertIn("NFR-API-RATE", nfunc_ids)

    def test_end_to_end_understand(self):
        prompt = "Create a database migrations schema for a student dashboard"
        requirement = self.urue.understand(prompt, self.wde_inventories)
        
        # Verify schema keys
        self.assertIn("business", requirement)
        self.assertIn("users", requirement)
        self.assertIn("modules", requirement)
        self.assertIn("requirements", requirement)
        self.assertIn("confidence", requirement)
        self.assertIn("evidence", requirement)
        self.assertIn("unknowns", requirement)
        self.assertIn("risks", requirement)
        self.assertIn("assumptions", requirement)
        
        # Check generated file
        out_file = self.workspace_path / ".aetheris" / "execution" / "requirement.json"
        self.assertTrue(out_file.exists())
        
        saved_data = json.loads(out_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_data["business"]["business_goal"], requirement["business"]["business_goal"])

if __name__ == "__main__":
    unittest.main()
