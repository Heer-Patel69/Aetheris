import unittest
import shutil
import json
from pathlib import Path
from intelligence.wde import (
    WorkspaceDiscoveryEngine, 
    IgnoreRuleManager, 
    DirectoryWalker, 
    FileFingerprintManager, 
    SchemaValidator
)

class TestWDE(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_wde_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create dummy directory structure
        (self.workspace_path / "src").mkdir(exist_ok=True)
        (self.workspace_path / "src" / "main.py").write_text("import sys\nprint('hello')", encoding="utf-8")
        (self.workspace_path / "package.json").write_text(json.dumps({
            "dependencies": {
                "next": "^14.0.0",
                "prisma": "^5.0.0"
            }
        }), encoding="utf-8")
        
        (self.workspace_path / ".gitignore").write_text("node_modules\n*.log\n", encoding="utf-8")
        (self.workspace_path / "ignored.log").write_text("ignore this file", encoding="utf-8")
        
        self.wde = WorkspaceDiscoveryEngine(str(self.workspace_path))

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_ignore_rule_manager(self):
        manager = IgnoreRuleManager(self.workspace_path)
        # Should ignore standard default
        self.assertTrue(manager.is_ignored(self.workspace_path / "node_modules"))
        self.assertTrue(manager.is_ignored(self.workspace_path / ".aetheris"))
        # Should ignore based on .gitignore file rule
        self.assertTrue(manager.is_ignored(self.workspace_path / "ignored.log"))
        # Should NOT ignore standard source code
        self.assertFalse(manager.is_ignored(self.workspace_path / "src" / "main.py"))

    def test_directory_walker(self):
        manager = IgnoreRuleManager(self.workspace_path)
        walker = DirectoryWalker(manager)
        files = walker.walk(self.workspace_path)
        
        # Should find package.json, main.py, .gitignore
        filenames = {f.name for f in files}
        self.assertIn("main.py", filenames)
        self.assertIn("package.json", filenames)
        # Should NOT find ignored.log
        self.assertNotIn("ignored.log", filenames)

    def test_file_fingerprint_manager(self):
        fpath = self.workspace_path / "src" / "main.py"
        h1 = FileFingerprintManager.calculate_sha256(fpath)
        self.assertTrue(len(h1) > 0)
        
        # Modify content and verify fingerprint changes
        fpath.write_text("import sys\nimport os", encoding="utf-8")
        h2 = FileFingerprintManager.calculate_sha256(fpath)
        self.assertNotEqual(h1, h2)

    def test_schema_validator(self):
        # Empty inventories should fail
        self.assertFalse(SchemaValidator.validate_wde_schemas({}))

    def test_end_to_end_scan(self):
        inventories = self.wde.scan()
        
        # Assert the 6 JSON inventory files exist in inventories dict
        self.assertIn("workspace.inventory", inventories)
        self.assertIn("filesystem.graph", inventories)
        self.assertIn("workspace.metadata", inventories)
        self.assertIn("language.inventory", inventories)
        self.assertIn("framework.inventory", inventories)
        self.assertIn("dependency.inventory", inventories)
        
        # Verify package manager is npm and prisma/nextjs frameworks are detected
        deps = inventories["dependency.inventory"]
        self.assertEqual(deps["package_manager"], "npm")
        self.assertIn("next", deps["dependencies"])
        
        frameworks = inventories["framework.inventory"]["frameworks"]
        self.assertIn("nextjs", frameworks)
        self.assertIn("prisma", frameworks)

if __name__ == "__main__":
    unittest.main()
