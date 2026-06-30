import unittest
import shutil
import json
from pathlib import Path
from kernel.planner import EngineeringPlanner
from kernel.goal_manager import EngineeringKnowledgeBase

class TestPlannerCapabilities(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_planner_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.ekb = EngineeringKnowledgeBase(self.workspace_path)
        self.planner = EngineeringPlanner(self.workspace_path)

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_planning_generation(self):
        # 1. Write mock universal blueprint
        blueprint = {
            "vision": "Build a secure auth system with DB",
            "inferred_subsystems": ["database_migrations", "authentication", "api_controllers", "unit_testing"]
        }
        self.ekb.save_artifact("universal.blueprint", blueprint)
        
        # 2. Write mock completeness report
        completeness = {
            "missing_requirements": [
                "Database schema structure could not be identified.",
                "User authorization/authentication features are not specified."
            ]
        }
        self.ekb.save_artifact("completeness.report", completeness)
        
        # 3. Generate plan
        sorted_tasks = self.planner.plan()
        
        # Assertions on sorted tasks (DAG)
        self.assertEqual(len(sorted_tasks), 4)
        # Auth must depend on database, unit_testing must depend on api
        self.assertTrue(sorted_tasks.index("database_migrations") < sorted_tasks.index("authentication"))
        self.assertTrue(sorted_tasks.index("api_controllers") < sorted_tasks.index("unit_testing"))
        
        # 4. Verify outputs are generated in .aetheris/
        execution_plan_file = self.workspace_path / ".aetheris" / "execution.plan.json"
        execution_graph_file = self.workspace_path / ".aetheris" / "execution.graph.json"
        execution_queue_file = self.workspace_path / ".aetheris" / "execution.queue.json"
        
        self.assertTrue(execution_plan_file.exists())
        self.assertTrue(execution_graph_file.exists())
        self.assertTrue(execution_queue_file.exists())
        
        # Load and verify content
        plan = json.loads(execution_plan_file.read_text(encoding="utf-8"))
        graph = json.loads(execution_graph_file.read_text(encoding="utf-8"))
        queue = json.loads(execution_queue_file.read_text(encoding="utf-8"))
        
        self.assertEqual(plan["goal"], "Build a secure auth system with DB")
        self.assertTrue(any(t["id"] == "task:authentication" for t in plan["tasks"]))
        
        # Check waves (concurrency queue)
        waves = queue["waves"]
        self.assertTrue(len(waves) >= 2)
        # First wave should be database_migrations because it has 0 in-degree
        self.assertIn("task:database_migrations", waves[0])

if __name__ == "__main__":
    unittest.main()
