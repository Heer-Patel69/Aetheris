import unittest
import shutil
from pathlib import Path
from kernel.goal_manager import GoalManager

class TestGoalManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary test workspace directory
        self.test_dir = Path("c:/AI/Agency owner/aetheris/scratch/test_workspace")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.goal_manager = GoalManager(self.test_dir)
        
        # Write dummy PRD.md
        self.prd_path = self.test_dir / "PRD.md"
        self.prd_path.write_text("""
# User Persona
- Student User: A high-school student looking to track homework.

# Business Rules
- Task deadline must be in the future.

# Feature List
- User Login Authentication
- Task CRUD operations
""", encoding="utf-8")

        # Write dummy schema.prisma
        self.prisma_path = self.test_dir / "schema.prisma"
        self.prisma_path.write_text("""
model User {
  id    Int    @id
  email String @unique
}
""", encoding="utf-8")

        # Write dummy Dockerfile
        self.docker_path = self.test_dir / "Dockerfile"
        self.docker_path.write_text("FROM alpine", encoding="utf-8")

    def tearDown(self):
        # Clean up temporary test workspace
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_expand_goal_discovery(self):
        understanding = self.goal_manager.expand_goal("Build a basic student app")
        
        # Assert database models discovered
        prisma_models = understanding["database_entities"]["prisma_models"]
        self.assertEqual(len(prisma_models), 1)
        self.assertEqual(prisma_models[0]["name"], "User")
        
        # Assert personas and business rules discovered
        self.assertTrue(any("Student User" in p["text"] for p in understanding["user_personas"]))
        self.assertTrue(any("Task deadline" in r["text"] for r in understanding["business_rules"]))
        self.assertTrue(any("User Login" in f["text"] for f in understanding["feature_inventory"]))
        
        # Assert confidence metrics computed from files
        self.assertEqual(understanding["confidence_scores"]["database"], 1.0)
        self.assertEqual(understanding["confidence_scores"]["docker"], 1.0)
        
        # Assert evidence lists files
        self.assertTrue(any("schema.prisma" in e for e in understanding["evidence"]))
        self.assertTrue(any("Dockerfile" in e for e in understanding["evidence"]))

if __name__ == "__main__":
    unittest.main()
