import unittest
import shutil
import json
from pathlib import Path
# pyrefly: ignore [missing-import]
from intelligence.ekb import EngineeringKnowledgeBase

class TestEKB(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_ekb_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.ekb = EngineeringKnowledgeBase(str(self.workspace_path))

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_register_and_get_object(self):
        content = {"id": "feat_01", "name": "Auth", "status": "draft"}
        obj_id = self.ekb.register_object("feature", content, producer="Test")
        self.assertEqual(obj_id, "feat_01")
        
        # Fetch current version
        obj = self.ekb.get_object(obj_id)
        self.assertIsNotNone(obj)
        self.assertEqual(obj["version"], 1)
        self.assertEqual(obj["content"]["status"], "draft")

    def test_versioning_updates(self):
        content_v1 = {"id": "feat_01", "name": "Auth", "status": "draft"}
        self.ekb.register_object("feature", content_v1)
        
        content_v2 = {"id": "feat_01", "name": "Auth", "status": "complete"}
        self.ekb.register_object("feature", content_v2)
        
        # Verify current version is 2
        curr = self.ekb.get_object("feat_01")
        self.assertEqual(curr["version"], 2)
        self.assertEqual(curr["content"]["status"], "complete")
        
        # Verify version 1 can be fetched separately
        v1 = self.ekb.get_object("feat_01", version=1)
        self.assertEqual(v1["version"], 1)
        self.assertEqual(v1["content"]["status"], "draft")

    def test_query_objects(self):
        self.ekb.register_object("feature", {"id": "f1", "status": "completed"})
        self.ekb.register_object("feature", {"id": "f2", "status": "pending"})
        
        results = self.ekb.query_objects({"status": "completed"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"]["id"], "f1")

    def test_integrity_failure(self):
        self.ekb.register_object("feature", {"id": "f1", "val": 10})
        # Tamper with the saved file
        fpath = self.ekb.kb_dir / "f1.json"
        data = json.loads(fpath.read_text(encoding="utf-8"))
        data["content"]["val"] = 99 # Tamper value
        fpath.write_text(json.dumps(data), encoding="utf-8")
        
        # Fetching should return None due to checksum validation failure
        self.assertIsNone(self.ekb.get_object("f1"))

if __name__ == "__main__":
    unittest.main()
