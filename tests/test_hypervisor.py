import os
import shutil
import unittest
import tempfile
from pathlib import Path

# Add src to sys.path
import sys
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from kernel.providers.registry import CapabilityRegistry
from kernel.providers.base import CompressionCapability, TemplateCapability, ExecutionCapability
from kernel.state import StateEngine
from kernel.event_bus import EventBus
from intelligence.ege import EngineeringGraphEngine
from validation.policy import PolicyEngine
from validation.dod import DoDEngine

class TestHypervisorCore(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_dir)
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_capability_registry(self):
        registry = CapabilityRegistry(str(self.workspace_path))
        # Clear any existing registrations for isolated test
        registry.clear()
        
        # Test lazy load of default capabilities
        compression = registry.resolve("compression")
        self.assertIsInstance(compression, CompressionCapability)
        
        templates = registry.resolve("templates")
        self.assertIsInstance(templates, TemplateCapability)
        
        hooks = registry.resolve("hooks")
        self.assertIsInstance(hooks, ExecutionCapability)
        
        with self.assertRaises(KeyError):
            registry.resolve("invalid_capability")

    def test_state_engine(self):
        state = StateEngine(str(self.workspace_path))
        state.initialize()
        
        # Verify subdirs are created
        self.assertTrue((self.workspace_path / ".aetheris" / "state").exists())
        self.assertTrue((self.workspace_path / ".aetheris" / "graphs").exists())
        self.assertTrue((self.workspace_path / ".aetheris" / "checkpoints").exists())
        
        # Test checkpoints
        checkpoint_data = {"task_id": "P1", "status": "COMPLETED"}
        state.save_checkpoint("P1", checkpoint_data)
        loaded = state.load_checkpoint("P1")
        self.assertEqual(loaded["task_id"], "P1")
        self.assertEqual(loaded["status"], "COMPLETED")
        
        # Test artifacts
        artifact_content = "import os\nprint('hello')"
        state.save_artifact("test_module.py", artifact_content, {"domain": "test"})
        loaded_art = state.load_artifact("test_module.py")
        self.assertEqual(loaded_art, artifact_content)
        
        meta = state.get_artifact_meta("test_module.py")
        self.assertEqual(meta["metadata"]["domain"], "test")
        self.assertTrue("checksum" in meta)

    def test_event_bus(self):
        event_bus = EventBus(str(self.workspace_path))
        
        received_events = []
        def handler(payload):
            received_events.append(payload)
            
        event_bus.subscribe("TestEvent", handler, "TestModule")
        event_bus.publish("TestEvent", "Publisher", {"data": "ok"})
        
        # Dispatch
        dispatched = event_bus.dispatch_next()
        self.assertTrue(dispatched)
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0]["data"], "ok")

    def test_graph_engine_subgraphs(self):
        ege = EngineeringGraphEngine(str(self.workspace_path))
        
        # Add node to a specific subgraph
        ege.add_subgraph_node("repository", "file:main.py", "File", {"size": 100})
        ege.add_subgraph_node("skill", "skill:backend-architect", "Skill", {"vibe": "expert"})
        ege.add_edge("file:main.py", "skill:backend-architect", "requires")
        
        # Check nodes are registered
        self.assertTrue(any(n["id"] == "file:main.py" for n in ege.nodes))
        subgraph_nodes = ege.get_subgraph_nodes("repository")
        self.assertEqual(len(subgraph_nodes), 1)
        self.assertEqual(subgraph_nodes[0]["id"], "file:main.py")

    def test_policy_engine(self):
        policy = PolicyEngine(str(self.workspace_path))
        
        # Test secret pattern rejection
        bad_code = "db_password = \"super_secret_123\""
        res = policy.validate_artifact("db.py", bad_code)
        self.assertFalse(res["success"])
        self.assertEqual(res["violations"][0]["rule"], "No Hardcoded Secrets")
        
        # Test clean code approval
        good_code = "import os\ndb_pass = os.environ.get('DB_PASS')"
        res_good = policy.validate_artifact("db.py", good_code)
        self.assertTrue(res_good["success"])

    def test_dod_engine(self):
        dod = DoDEngine(str(self.workspace_path))
        
        # Fail if state does not exist
        res = dod.verify_wave(["database_migrations"])
        self.assertFalse(res["success"])
        
        # Initialize and test completed status
        state = StateEngine(str(self.workspace_path))
        state.initialize()
        
        checkpoint_data = {
            "tasks": [
                {"name": "database_migrations", "status": "Completed"},
                {"name": "authentication", "status": "Running"}
            ]
        }
        state.save_checkpoint("execution_state", checkpoint_data)
        # Verify compatibility copy works
        compat_file = self.workspace_path / ".aetheris" / "execution_state.json"
        import json
        compat_file.write_text(json.dumps(checkpoint_data), encoding="utf-8")
        
        res_wave = dod.verify_wave(["database_migrations"])
        self.assertTrue(res_wave["success"])
        
        res_running = dod.verify_wave(["authentication"])
        self.assertFalse(res_running["success"])
