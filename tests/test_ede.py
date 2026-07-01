import unittest
import shutil
import json
from pathlib import Path
# pyrefly: ignore [missing-import]
from intelligence.ekb import EngineeringKnowledgeBase
# pyrefly: ignore [missing-import]
from intelligence.ede import EngineeringDecisionEngine

class TestEDE(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_ede_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.ekb = EngineeringKnowledgeBase(str(self.workspace_path))
        self.ede = EngineeringDecisionEngine(str(self.workspace_path), self.ekb)

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_evaluate_decision(self):
        # PostgreSQL should score higher than SQLite under performance weight
        weights = {"perf": 0.8, "cost": 0.1, "maint": 0.1, "evidence": 0.0}
        dec = self.ede.evaluate_decision("database", ["PostgreSQL", "SQLite"], weights=weights)
        
        self.assertEqual(dec["selected_option"], "PostgreSQL")
        
        # Verify registered as object in EKB
        objs = self.ekb.query_objects({"type": "decision"})
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0]["content"]["selected_option"], "PostgreSQL")

    def test_evaluate_decision_sqlite(self):
        # SQLite should score higher under cost weight
        weights = {"perf": 0.1, "cost": 0.8, "maint": 0.1, "evidence": 0.0}
        dec = self.ede.evaluate_decision("database", ["PostgreSQL", "SQLite"], weights=weights)
        self.assertEqual(dec["selected_option"], "SQLite")

    def test_decision_rollback(self):
        # Save version 1: PostgreSQL
        weights_v1 = {"perf": 0.8, "cost": 0.1, "maint": 0.1, "evidence": 0.0}
        self.ede.evaluate_decision("database", ["PostgreSQL", "SQLite"], weights=weights_v1)
        
        # Save version 2: SQLite
        weights_v2 = {"perf": 0.1, "cost": 0.8, "maint": 0.1, "evidence": 0.0}
        self.ede.evaluate_decision("database", ["PostgreSQL", "SQLite"], weights=weights_v2)
        
        # Verify current version is version 2 (SQLite)
        curr = self.ekb.get_object("dec_database")
        self.assertEqual(curr["version"], 2)
        self.assertEqual(curr["content"]["selected_option"], "SQLite")
        
        # Rollback database decision to version 1 (PostgreSQL)
        restored = self.ede.rollback_decision("database", target_version=1)
        self.assertIsNotNone(restored)
        self.assertEqual(restored["selected_option"], "PostgreSQL")
        
        # Verify EKB current object is version 3 with PostgreSQL content
        latest = self.ekb.get_object("dec_database")
        self.assertEqual(latest["version"], 3)
        self.assertEqual(latest["content"]["selected_option"], "PostgreSQL")

if __name__ == "__main__":
    unittest.main()
