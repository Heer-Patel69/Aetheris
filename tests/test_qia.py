import unittest
import shutil
import json
from pathlib import Path
from intelligence.ekb import EngineeringKnowledgeBase
from intelligence.ege import EngineeringGraphEngine
from intelligence.qia import (
    QueryAndImpactAnalysisEngine,
    QueryParser,
    IntentResolver,
    GraphTraversalEngine
)

class TestQIA(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_qia_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        self.ekb = EngineeringKnowledgeBase(str(self.workspace_path))
        self.ege = EngineeringGraphEngine(str(self.workspace_path))
        self.qia = QueryAndImpactAnalysisEngine(str(self.workspace_path), self.ekb, self.ege)
        
        # Build dummy nodes & edges
        self.ege.add_node("layer:domain", "ArchitectureLayer")
        self.ege.add_node("layer:application", "ArchitectureLayer")
        self.ege.add_node("layer:infrastructure", "ArchitectureLayer")
        
        # infrastructure -> application -> domain
        self.ege.add_edge("layer:infrastructure", "layer:application", "depends_on")
        self.ege.add_edge("layer:application", "layer:domain", "depends_on")

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_query_parser(self):
        parsed = QueryParser.parse("What breaks if database changes?")
        self.assertEqual(parsed["target"], "layer:infrastructure")
        
        parsed2 = QueryParser.parse("Which services depend on auth?")
        self.assertEqual(parsed2["target"], "layer:application")

    def test_intent_resolver(self):
        self.assertEqual(IntentResolver.resolve("What breaks if domain changes?"), "IMPACT")
        self.assertEqual(IntentResolver.resolve("Which modules depend on User?"), "DEPENDENCY")
        self.assertEqual(IntentResolver.resolve("List all registered models"), "LOOKUP")

    def test_graph_traversal_dependents(self):
        traverser = GraphTraversalEngine(self.ege)
        # dependents of domain should be application, infrastructure (inverted BFS)
        # Wait, the edge is: A depends_on B (A -> B).
        # A depends on B, so if B changes, it impacts A.
        # Edges: infra depends_on app (infra -> app). app depends_on domain (app -> domain).
        # Dependents of domain: app, and then infra (since infra depends on app, app depends on domain).
        dependents = traverser.get_dependents("layer:domain")
        self.assertIn("layer:application", dependents)
        self.assertIn("layer:infrastructure", dependents)
        self.assertEqual(len(dependents), 2)

    def test_end_to_end_query_impact(self):
        # Querying impact on database (layer:infrastructure)
        # infra has no dependents (nothing depends on infra in this mock direction)
        res = self.qia.query("What breaks if database changes?")
        self.assertEqual(res["intent"], "IMPACT")
        self.assertEqual(res["confidence"], 0.90)
        
        # Verify query.index.json written
        index_file = self.workspace_path / ".aetheris" / "execution" / "query.index.json"
        self.assertTrue(index_file.exists())
        saved = json.loads(index_file.read_text(encoding="utf-8"))
        self.assertEqual(saved["intent"], "IMPACT")

    def test_analyze_impact_cascade(self):
        report = self.qia.analyze_impact("layer:domain")
        self.assertEqual(report["target_node"], "layer:domain")
        self.assertEqual(report["total_affected"], 2)
        
        # Verify impact.index.json written
        impact_file = self.workspace_path / ".aetheris" / "execution" / "impact.index.json"
        self.assertTrue(impact_file.exists())
        saved = json.loads(impact_file.read_text(encoding="utf-8"))
        self.assertEqual(saved["total_affected"], 2)

if __name__ == "__main__":
    unittest.main()
