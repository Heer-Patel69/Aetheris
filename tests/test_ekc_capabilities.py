import unittest
import shutil
import json
import time
from pathlib import Path
from kernel.goal_manager import EngineeringKnowledgeCompiler, EventBus

class TestEKCCapabilities(unittest.TestCase):
    def setUp(self):
        # Create a temporary workspace
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_ekc_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Capture events
        self.events_fired = []
        self.event_bus = EventBus(self.workspace_path)
        
        # Subscribe handler to capture all events
        def event_handler(payload):
            self.events_fired.append(payload)
            
        self.event_bus.register_subscriber("test_module", "DiscoveryStarted", event_handler)
        self.event_bus.register_subscriber("test_module", "LanguageParsed", event_handler)
        self.event_bus.register_subscriber("test_module", "GraphUpdated", event_handler)
        self.event_bus.register_subscriber("test_module", "CompilationFinished", event_handler)
        
        self.compiler = EngineeringKnowledgeCompiler(self.workspace_path, self.event_bus)

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_complete_compiler_passes(self):
        # Write dummy files representing different languages
        (self.workspace_path / "PRD.md").write_text("""
# User Persona
- Student User: Tracks schedules.

# Business Rules
- Deadline must be valid.

# Feature List
- User Login Authentication
        """, encoding="utf-8")
        
        (self.workspace_path / "schema.prisma").write_text("""
model User {
  id    Int    @id
  email String @unique
}
        """, encoding="utf-8")
        
        (self.workspace_path / "main.py").write_text("""
import sys
class ApplicationController:
    def start(self):
        pass
        """, encoding="utf-8")
        
        # Compile
        success = self.compiler.compile("Test Product")
        self.assertTrue(success)
        
        # Drain the event bus queue
        while self.event_bus.dispatch_next():
            pass
            
        # Assert events fired
        self.assertTrue(any(Path(e.get("workspace")).resolve() == self.workspace_path.resolve() for e in self.events_fired if "workspace" in e))
        self.assertTrue(any(e.get("file") == "PRD.md" for e in self.events_fired))
        self.assertTrue(any(e.get("file") == "schema.prisma" for e in self.events_fired))
        self.assertTrue(any(e.get("file") == "main.py" for e in self.events_fired))
        
        # Verify EKB existence and abstractions
        graph = self.compiler.ekb.load_artifact("engineering.graph")
        self.assertIsNotNone(graph)
        self.assertTrue(any(n["id"] == "file:main.py" for n in graph["nodes"]))
        self.assertTrue(any(n["id"] == "symbol:prisma_model:User" for n in graph["nodes"]))
        
        # Query Engine check
        models = self.compiler.query("get_database_models")
        self.assertIn("User", models)
        
        dependencies = self.compiler.query("get_dependencies", {"node_id": "file:main.py"})
        self.assertIn("import:sys", dependencies)
        
        # Incremental compilation check
        # Clear events list
        self.events_fired.clear()
        
        # Modifying main.py
        time.sleep(1) # Ensure modification time changes
        (self.workspace_path / "main.py").write_text("""
import os
import sys
class ApplicationController:
    def stop(self):
        pass
        """, encoding="utf-8")
        
        # Compile incrementally
        self.compiler.compile("Test Product")
        
        # Diagnostics
        diag = self.compiler.diagnostics()
        self.assertEqual(diag["cache_stats"]["hits"], 2) # PRD.md, schema.prisma unchanged
        self.assertEqual(diag["cache_stats"]["misses"], 1) # main.py compiled
        
        # Deletion pruning check
        (self.workspace_path / "schema.prisma").unlink()
        self.compiler.compile("Test Product")
        
        # Verify User model pruned
        graph_after_deletion = self.compiler.ekb.load_artifact("engineering.graph")
        self.assertFalse(any(n["id"] == "file:schema.prisma" for n in graph_after_deletion["nodes"]))
        
        # Verify Reference validation
        valid = self.compiler.validate()
        self.assertTrue(valid)

if __name__ == "__main__":
    unittest.main()
