import unittest
import shutil
import json
from pathlib import Path
from intelligence.ege import EngineeringGraphEngine

class TestEGE(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_ege_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.ege = EngineeringGraphEngine(str(self.workspace_path))

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_add_nodes_and_edges(self):
        self.ege.add_node("req:FR1", "Requirement")
        self.ege.add_node("file:src/auth.py", "File")
        self.ege.add_edge("file:src/auth.py", "req:FR1", "implements")
        
        self.assertEqual(len(self.ege.nodes), 2)
        self.assertEqual(len(self.ege.edges), 1)

    def test_cycle_detection(self):
        self.ege.add_node("A", "Task")
        self.ege.add_node("B", "Task")
        self.ege.add_node("C", "Task")
        
        self.ege.add_edge("A", "B", "depends")
        self.ege.add_edge("B", "C", "depends")
        self.ege.add_edge("C", "A", "depends")
        
        cycles = self.ege.detect_cycles()
        self.assertEqual(len(cycles), 1)
        self.assertIn("A -> B -> C -> A", cycles)

    def test_impact_analysis(self):
        self.ege.add_node("db", "Database")
        self.ege.add_node("auth", "Auth")
        self.ege.add_node("api", "API")
        self.ege.add_node("fe", "Frontend")
        
        # fe depends on api, api depends on auth, auth depends on db
        self.ege.add_edge("fe", "api", "depends")
        self.ege.add_edge("api", "auth", "depends")
        self.ege.add_edge("auth", "db", "depends")
        
        # Impacting db should propagate to all dependents (auth, api, fe)
        impacted = self.ege.get_impacted_nodes("db")
        self.assertIn("auth", impacted)
        self.assertIn("api", impacted)
        self.assertIn("fe", impacted)
        self.assertEqual(len(impacted), 3)

    def test_isolated_nodes(self):
        self.ege.add_node("active1", "Task")
        self.ege.add_node("active2", "Task")
        self.ege.add_node("dead", "Task")
        self.ege.add_edge("active1", "active2", "depends")
        
        isolated = self.ege.get_isolated_nodes()
        self.assertEqual(isolated, ["dead"])

if __name__ == "__main__":
    unittest.main()
