import unittest
import shutil
import json
from pathlib import Path
from intelligence.ekb import EngineeringKnowledgeBase
from execution.tde import TaskDecompositionEngine
from execution.dgb import DependencyGraphBuilder
from execution.sse import SkillSelectionEngine

class TestExecution(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_execution_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.ekb = EngineeringKnowledgeBase(str(self.workspace_path))
        
        self.tde = TaskDecompositionEngine(str(self.workspace_path), self.ekb)
        self.dgb = DependencyGraphBuilder(str(self.workspace_path), self.ekb)
        self.sse = SkillSelectionEngine(str(self.workspace_path), self.ekb)

        self.blueprint = {
            "summary": {
                "database_engine": "PostgreSQL"
            }
        }

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_task_decomposition_engine(self):
        exec_tree = self.tde.generate_tasks(self.blueprint)
        
        # Verify execution files created
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "tasks.json").exists())
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "modules.json").exists())
        
        # Verify tasks mapping details
        tasks = exec_tree["tasks"]
        self.assertEqual(len(tasks), 2)
        task_ids = {t["id"] for t in tasks}
        self.assertIn("task_db_init", task_ids)
        self.assertIn("task_auth_pipeline", task_ids)

        # Test splitting task
        subtasks = self.tde.split_task("task_db_init", "high effort")
        self.assertEqual(len(subtasks), 2)
        self.assertEqual(subtasks[0]["id"], "task_db_init_sub1")
        self.assertEqual(subtasks[0]["estimated_effort_hours"], 2.0)

    def test_dependency_graph_builder(self):
        exec_tree = self.tde.generate_tasks(self.blueprint)
        tasks = exec_tree["tasks"]
        
        graph = self.dgb.build_graph(tasks)
        
        # Verify nodes and edges
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(len(graph["edges"]), 1)
        
        # Verify topological sort order
        order = self.dgb.get_topological_order()
        self.assertEqual(order[0], "task_db_init")
        self.assertEqual(order[1], "task_auth_pipeline")
        
        # Verify parallel groupings (task_db_init must execute first)
        groups = self.dgb.get_parallel_groups()
        self.assertEqual(groups[0][0], "task_db_init")
        self.assertEqual(groups[1][0], "task_auth_pipeline")

        # Test cycle detection on circular graph
        circular_tasks = [
            {"id": "t1", "dependencies": ["t2"], "estimated_effort_hours": 1.0},
            {"id": "t2", "dependencies": ["t1"], "estimated_effort_hours": 1.0}
        ]
        with self.assertRaises(ValueError):
            self.dgb.build_graph(circular_tasks)

    def test_skill_selection_engine(self):
        exec_tree = self.tde.generate_tasks(self.blueprint)
        tasks = exec_tree["tasks"]
        
        report = self.sse.select_skills(tasks)
        
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "task.skills.map.json").exists())
        self.assertEqual(len(report["mappings"]), 2)
        
        db_mapping = next(m for m in report["mappings"] if m["task_id"] == "task_db_init")
        self.assertEqual(db_mapping["selected_skills"][0]["name"], "agency-database-optimizer")

    def test_model_routing_engine(self):
        from execution.mre import ModelRoutingEngine
        mre = ModelRoutingEngine(str(self.workspace_path), self.ekb)
        task = {"id": "task_db_init", "priority": "HIGH"}
        
        decision = mre.route_model(task, {"name": "agency-database-optimizer"})
        self.assertEqual(decision["primary_model"], "claude-3-5-sonnet")
        self.assertTrue(decision["estimated_cost_usd"] > 0)
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "model.assignment.json").exists())

    def test_context_assembly_engine(self):
        from execution.cae import ContextAssemblyEngine
        cae = ContextAssemblyEngine(str(self.workspace_path), self.ekb)
        task = {"id": "task_db_init"}
        
        ctx = cae.assemble_context(task, [])
        self.assertEqual(ctx["task_id"], "task_db_init")
        self.assertTrue(ctx["assembled_tokens_count"] > 0)
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "execution.context.json").exists())

    def test_execution_scheduler(self):
        from execution.es import ExecutionScheduler
        es = ExecutionScheduler(str(self.workspace_path), self.ekb)
        dag = {"order": ["task_db_init", "task_auth_pipeline"]}
        
        plan = es.schedule(dag, {})
        self.assertEqual(plan["total_steps"], 2)
        self.assertEqual(plan["queue"][0]["parallel_tasks"][0]["task_id"], "task_db_init")
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "execution.queue.json").exists())

    def test_parallel_execution_engine(self):
        from execution.pee import ParallelExecutionEngine
        pee = ParallelExecutionEngine(str(self.workspace_path), self.ekb)
        queue = [{
            "step": 1,
            "parallel_tasks": [{"task_id": "task_db_init"}]
        }]
        
        plan = pee.create_batches(queue)
        self.assertEqual(len(plan["batches"]), 1)
        self.assertEqual(plan["batches"][0]["locked_files"][0], "database.plan.json")
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "parallel.execution.plan.json").exists())

    def test_autonomous_code_generation_engine(self):
        from execution.acge import AutonomousCodeGenerationEngine
        acge = AutonomousCodeGenerationEngine(str(self.workspace_path), self.ekb)
        task = {"id": "task_db_init"}
        
        report = acge.generate_code(task, {})
        self.assertEqual(len(report["modified_files"]), 1)
        self.assertEqual(report["modified_files"][0]["action"], "create")
        self.assertTrue((self.workspace_path / "src" / "db_init_bootstrap.sql").exists())

    def test_self_review_engine(self):
        from execution.sre import SelfReviewEngine
        sre = SelfReviewEngine(str(self.workspace_path), self.ekb)
        files = [{
            "path": "src/auth_middleware.py",
            "action": "create"
        }]
        
        report = sre.review(files)
        self.assertEqual(report["approved"], True)
        self.assertEqual(report["overall_quality_score"], 95.0)
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "engineering.review.json").exists())

    def test_patch_recovery_engine(self):
        from execution.pre import PatchRecoveryEngine
        pre = PatchRecoveryEngine(str(self.workspace_path), self.ekb)
        failure = {"error": "SyntaxError: invalid syntax"}
        
        plan = pre.recover(failure)
        self.assertEqual(plan["patches"][0]["error_classification"], "SYNTAX_ERROR")
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "patch.plan.json").exists())

    def test_state_persistence_engine(self):
        from execution.spe import StatePersistenceEngine
        spe = StatePersistenceEngine(str(self.workspace_path), self.ekb)
        state = {"blueprint_version": 2, "completed_tasks": ["task_db_init"], "active_task_id": "task_auth_pipeline"}
        
        chk = spe.checkpoint(state)
        self.assertEqual(chk["blueprint_version"], 2)
        self.assertEqual(chk["active_task_id"], "task_auth_pipeline")
        
        restored = spe.load_state()
        self.assertEqual(restored["active_task_id"], "task_auth_pipeline")

    def test_git_operations_engine(self):
        from execution.goe import GitOperationsEngine
        goe = GitOperationsEngine(str(self.workspace_path), self.ekb)
        
        commit_plan = goe.commit("task_db_init", "Verify user DB setup", ["src/db_init_bootstrap.sql"])
        self.assertEqual(commit_plan["files_staged"][0], "src/db_init_bootstrap.sql")
        self.assertIn("task_db_init", commit_plan["commit_message"])
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "git.plan.json").exists())

    def test_documentation_generation_engine(self):
        from execution.dge import DocumentationGenerationEngine
        dge = DocumentationGenerationEngine(str(self.workspace_path), self.ekb)
        
        metrics = dge.generate_documentation([{"decision": "Config db", "reason": "baseline"}])
        self.assertEqual(metrics["broken_links_count"], 0)
        self.assertTrue((self.workspace_path / "README.md").exists())
        self.assertTrue((self.workspace_path / "docs" / "adr" / "0001_decision.md").exists())

    def test_execution_metrics_engine(self):
        from execution.eme import ExecutionMetricsEngine
        eme = ExecutionMetricsEngine(str(self.workspace_path), self.ekb)
        
        eme.record_metric("total_execution_seconds", 3.5)
        eme.record_metric("cost_usd", 0.02)
        dashboard = eme.generate_dashboard()
        self.assertEqual(dashboard["cost_usd"], 0.02)
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "execution.metrics.json").exists())

    def test_execution_orchestrator(self):
        from execution.eo import ExecutionOrchestrator
        eo = ExecutionOrchestrator(str(self.workspace_path), self.ekb)
        
        state = eo.run(str(self.workspace_path), "run all")
        self.assertEqual(state["current_lifecycle_state"], "Completed")
        self.assertTrue((self.workspace_path / ".aetheris" / "execution" / "orchestrator.state.json").exists())

if __name__ == "__main__":
    unittest.main()
