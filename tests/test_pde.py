import unittest
import shutil
import json
from pathlib import Path
from intelligence.pde import (
    ProductDiscoveryEngine,
    PromptEvidenceMerger,
    DomainClassifier,
    PersonaDiscoveryEngine,
    ComplexityEstimator
)

class TestPDE(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_pde_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.pde = ProductDiscoveryEngine(str(self.workspace_path))
        
        self.wde_inventories = {
            "workspace.metadata": {"total_files": 5},
            "language.inventory": {"languages": {"python": {"file_count": 5}}},
            "framework.inventory": {"frameworks": {}},
            "dependency.inventory": {"package_manager": "pip", "dependencies": {}}
        }
        
        self.requirement = {
            "business": {
                "business_goal": "Compile customer logs",
                "business_objectives": ["Obj1", "Obj2"]
            },
            "users": {
                "personas": [
                    {"name": "Developer User", "role": "Write code", "goals": ["Write tests"]},
                    {"name": "developer user", "role": "Duplicates developer role", "goals": ["Code"]}
                ]
            },
            "requirements": {
                "functional": [
                    {"id": "FR-DB", "name": "DB migration helper", "priority": "HIGH", "description": "Helper"},
                    {"id": "FR-API", "name": "API routes controller", "priority": "LOW", "description": "Controller"}
                ],
                "non_functional": [
                    {"id": "NFR-SEC", "name": "Security audit logs", "description": "Logs"}
                ]
            }
        }

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_prompt_evidence_merger(self):
        merged = PromptEvidenceMerger.merge(self.requirement, self.wde_inventories)
        self.assertEqual(merged["total_files"], 5)
        self.assertIn("python", merged["languages"])

    def test_domain_classifier(self):
        domain = DomainClassifier.classify({"languages": ["python"], "frameworks": []})
        self.assertEqual(domain, "Scientific Computing / CLI Domain")

    def test_persona_discovery_engine(self):
        # Case insensitive deduplication
        personas = PersonaDiscoveryEngine.discover(self.requirement)
        self.assertEqual(len(personas), 1)
        self.assertEqual(personas[0]["name"], "Developer User")

    def test_complexity_estimator(self):
        est = ComplexityEstimator.estimate([{"id": "F1"}, {"id": "F2"}])
        self.assertEqual(est["complexity"], "LOW")
        self.assertEqual(est["effort_hours"], 40)

    def test_end_to_end_discover(self):
        plan = self.pde.discover(self.requirement, self.wde_inventories)
        self.assertIn("product_name", plan)
        self.assertIn("flows", plan)
        self.assertIn("features", plan)
        self.assertEqual(plan["product_name"], "Compile customer logs")
        
        # Verify JSON file generated
        out_file = self.workspace_path / ".aetheris" / "execution" / "product.plan.json"
        self.assertTrue(out_file.exists())
        saved = json.loads(out_file.read_text(encoding="utf-8"))
        self.assertEqual(saved["product_name"], "Compile customer logs")

if __name__ == "__main__":
    unittest.main()
