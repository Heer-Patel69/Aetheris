import unittest
import shutil
import json
from pathlib import Path
from intelligence.ape import (
    ArchitecturePlanningEngine,
    ArchitectureStyleSelector,
    DomainBoundaryPlanner,
    StoragePlanner,
    ArchitectureValidator
)

class TestAPE(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_ape_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.ape = ArchitecturePlanningEngine(str(self.workspace_path))
        
        self.product_plan = {
            "product_name": "Test Platform",
            "category": "Web Front-End SaaS Domain",
            "estimates": {"complexity": "HIGH"},
            "features": [
                {"id": "FR-AUTH", "name": "Authentication module", "scope": "MVP"},
                {"id": "FR-DB", "name": "Database migrations schema", "scope": "MVP"}
            ]
        }

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_style_selector(self):
        style = ArchitectureStyleSelector.select(self.product_plan)
        self.assertIn("Clean Domain-Driven Design", style)

    def test_domain_boundary_planner(self):
        boundaries = DomainBoundaryPlanner.group(self.product_plan)
        contexts = {b["context"] for b in boundaries}
        self.assertIn("IdentityAccessContext", contexts)
        self.assertIn("PersistenceContext", contexts)

    def test_storage_planner(self):
        storage = StoragePlanner.plan(self.product_plan)
        self.assertEqual(storage["database"], "PostgreSQL")
        self.assertEqual(storage["orm"], "Prisma")
        self.assertTrue(storage["caching"]["enabled"])

    def test_architecture_validator(self):
        # 1. Valid graph
        graph = {
            "nodes": [
                {"id": "layer:infrastructure"},
                {"id": "layer:application"},
                {"id": "layer:domain"}
            ],
            "edges": [
                {"source": "layer:infrastructure", "target": "layer:application"},
                {"source": "layer:application", "target": "layer:domain"}
            ]
        }
        valid, errors = ArchitectureValidator.validate(graph)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
        
        # 2. Cycle graph detection
        cycle_graph = {
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [
                {"source": "A", "target": "B"},
                {"source": "B", "target": "A"}
            ]
        }
        valid, errors = ArchitectureValidator.validate(cycle_graph)
        self.assertFalse(valid)
        self.assertTrue(any("cycle detected" in err.lower() for err in errors))

        # 3. DDD Layer Violation check
        violation_graph = {
            "nodes": [{"id": "domain:User"}, {"id": "infra:Database"}],
            "edges": [
                {"source": "domain:User", "target": "infra:Database"} # domain depends on infra - VIOLATION
            ]
        }
        valid, errors = ArchitectureValidator.validate(violation_graph)
        self.assertFalse(valid)
        self.assertTrue(any("layer violation" in err.lower() for err in errors))

    def test_end_to_end_plan(self):
        plan, graph = self.ape.plan(self.product_plan)
        self.assertEqual(plan["style"], "Clean Domain-Driven Design (DDD) Architecture")
        self.assertIn("src/domain", plan["folder_structure"])
        
        # Verify output files generated
        plan_file = self.workspace_path / ".aetheris" / "execution" / "architecture.plan.json"
        graph_file = self.workspace_path / ".aetheris" / "execution" / "architecture.graph.json"
        
        self.assertTrue(plan_file.exists())
        self.assertTrue(graph_file.exists())
        
        saved_plan = json.loads(plan_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_plan["style"], plan["style"])

if __name__ == "__main__":
    unittest.main()
