import unittest
import shutil
import json
from pathlib import Path
from intelligence.cost_analyzer import CostAnalyzer
from intelligence.token_intelligence import TokenIntelligence
from intelligence.repository_metrics import RepositoryMetrics
from intelligence.context_optimizer import ContextOptimizer
from intelligence.historical_analytics import HistoricalAnalytics
from intelligence.dashboard_metrics import DashboardMetrics
from intelligence.benchmark_engine import BenchmarkEngine

class TestATIB(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_atib_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create a mock repository structure inside test_atib_workspace
        (self.workspace_path / "src").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "tests").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "skills").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "rfcs").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "specs").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "docs").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "architecture").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "security").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "deployment").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "accessibility").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "benchmarks").mkdir(parents=True, exist_ok=True)
        
        # Write dummy files
        (self.workspace_path / "src" / "db.py").write_text("import sqlite3\n# Duplicate comment\n# Duplicate comment\n# DB connection setup", encoding="utf-8")
        (self.workspace_path / "src" / "frontend_view.py").write_text("import ui", encoding="utf-8")
        (self.workspace_path / "tests" / "test_db.py").write_text("def test_dummy(): assert True", encoding="utf-8")
        (self.workspace_path / "skills" / "database_skill.md").write_text("Database capability description", encoding="utf-8")
        (self.workspace_path / "rfcs" / "RFC-001.md").write_text("RFC definitions", encoding="utf-8")
        (self.workspace_path / "specs" / "SPEC-001.md").write_text("SPEC contracts", encoding="utf-8")
        (self.workspace_path / "docs" / "README.md").write_text("Documentation content", encoding="utf-8")
        (self.workspace_path / "architecture" / "adr-001.md").write_text("ADR 1", encoding="utf-8")
        (self.workspace_path / "security" / "auth.py").write_text("secure", encoding="utf-8")
        (self.workspace_path / "deployment" / "dockerfile").write_text("FROM python", encoding="utf-8")
        (self.workspace_path / "accessibility" / "wcag.txt").write_text("accessible", encoding="utf-8")
        (self.workspace_path / "benchmarks" / "perf_test.py").write_text("benchmark", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.workspace_path, ignore_errors=True)

    def test_cost_analyzer(self):
        analyzer = CostAnalyzer()
        cost_flash = analyzer.calculate_cost("gemini-1.5-flash", 100_000, 20_000)
        # 100k input * 0.075 / 1M = 0.0075
        # 20k output * 0.30 / 1M = 0.006
        # Total = 0.0135
        self.assertEqual(cost_flash, 0.0135)
        
        # Custom fallback
        cost_custom = analyzer.calculate_cost("unsupported-model", 100_000, 20_000)
        self.assertGreater(cost_custom, 0.0)

    def test_token_intelligence(self):
        intel = TokenIntelligence("gemini-1.5-flash")
        res = intel.track_request(
            input_tokens=1000,
            output_tokens=200,
            cached_tokens=100,
            reasoning_tokens=50,
            latency=1.5,
            streaming_duration=1.2,
            retry_count=1,
            error_occurred=False,
            prompt_size=5000,
            completion_size=1000,
            context_limit=100_000
        )
        self.assertEqual(res["total_tokens"], 1200)
        self.assertEqual(res["cached_tokens"], 100)
        self.assertEqual(res["reasoning_tokens"], 50)
        self.assertEqual(res["context_window_usage_pct"], 1.0)
        
        summary = intel.get_summary()
        self.assertEqual(summary["api_calls"], 1)
        self.assertEqual(summary["retry_count"], 1)
        self.assertEqual(summary["errors"], 0)

    def test_repository_metrics(self):
        metrics_eng = RepositoryMetrics(str(self.workspace_path))
        files_used = ["src/db.py", "skills/database_skill.md", "rfcs/RFC-001.md", "specs/SPEC-001.md"]
        metrics = metrics_eng.calculate_metrics(files_used)
        
        self.assertEqual(metrics["total_files"], 12)
        self.assertEqual(metrics["files_used"], 4)
        self.assertEqual(metrics["files_ignored"], 8)
        
        cov = metrics["coverage"]
        self.assertEqual(cov["repository_coverage"], round((4 / 12) * 100, 2))
        self.assertEqual(cov["skill_coverage"], 100.0)
        self.assertEqual(cov["rfc_coverage"], 100.0)
        self.assertEqual(cov["spec_coverage"], 100.0)
        
        # We created database, source, test, docs, specs, rfcs files
        self.assertEqual(cov["database_coverage"], 100.0)
        self.assertEqual(cov["testing_coverage"], 100.0)
        
        # Score checks
        self.assertGreater(metrics["engineering_score"], 50.0)

    def test_context_optimizer(self):
        opt = ContextOptimizer(str(self.workspace_path))
        available_files = [
            {"path": "src/db.py", "content": "import sqlite3\n# Comment\n# Comment\n# Comment\nconnect()"},
            {"path": "tests/test_db.py", "content": "def test()"}
        ]
        
        # Test duplicate comment line removal inside large files logic (simulated by reducing size check to run duplicates filter)
        # Set content size large enough to trigger cleanup
        available_files[0]["content"] = available_files[0]["content"] + ("\n" * 11000) + "\n# Comment\n# Comment"
        
        res = opt.optimize_context(
            task_desc="Update sqlite database schema connections",
            available_files=available_files,
            available_skills=["database-engineer", "ui-designer"],
            available_specs=["SPEC-001", "SPEC-002"],
            available_rfcs=["RFC-001"]
        )
        
        self.assertIn("src/db.py", [f["path"] for f in res["selected_files"]])
        self.assertIn("database-engineer", res["selected_skills"])
        self.assertNotIn("ui-designer", res["selected_skills"])
        self.assertGreater(res["reduction_percentage"], 0.0)

    def test_historical_analytics(self):
        analytics = HistoricalAnalytics(str(self.workspace_path))
        
        run_data = {
            "model": "gemini-1.5-flash",
            "input_tokens": 5000,
            "output_tokens": 1000,
            "total_tokens": 6000,
            "cached_tokens": 500,
            "reasoning_tokens": 200,
            "cost": 0.001,
            "latency": 2.5,
            "repository_size_bytes": 10000,
            "total_files": 100,
            "files_used": 10,
            "skills_scanned": 5,
            "skills_used": 2,
            "rfcs_used": 1,
            "specs_used": 1,
            "repository_coverage": 10.0,
            "skill_utilization": 40.0,
            "rfc_utilization": 20.0,
            "spec_utilization": 20.0,
            "context_reduction": 80.0,
            "engineering_score": 90.0,
            "production_readiness": 100.0
        }
        
        analytics.record_session(run_data)
        
        # Verify history file exists
        self.assertTrue(analytics.history_file.exists())
        
        # Verify trend reports exported
        self.assertTrue((analytics.reports_dir / "token_report.json").exists())
        self.assertTrue((analytics.reports_dir / "benchmark.json").exists())
        self.assertTrue((analytics.reports_dir / "historical_trends.json").exists())
        
        trends = analytics.calculate_trends()
        self.assertEqual(trends["average_tokens_per_project"], 6000.0)
        self.assertEqual(trends["average_cost"], 0.001)

    def test_dashboard_metrics(self):
        dash = DashboardMetrics()
        token_summary = {"model": "gemini-1.5-flash", "total_tokens": 1200, "cost": 0.0001, "latency": 1.2, "context_window_usage_pct": 2.5}
        repo_summary = {
            "repository_size_bytes": 5000, "total_files": 10, "files_used": 3, "engineering_score": 85.0,
            "coverage": {"repository_coverage": 30.0, "skill_coverage": 50.0, "rfc_coverage": 25.0, "spec_coverage": 25.0, "deployment_coverage": 100.0}
        }
        trends = {"average_tokens_per_project": 5000.0, "average_cost": 0.001}
        
        res = dash.generate_dashboard(token_summary, repo_summary, trends)
        self.assertEqual(res["current_model"], "gemini-1.5-flash")
        self.assertEqual(res["engineering_score"], 85.0)
        self.assertEqual(res["production_readiness"], 100.0)

    def test_benchmark_engine(self):
        bench = BenchmarkEngine()
        token_summary = {"input_tokens": 800, "output_tokens": 200, "cost": 0.0002, "latency": 0.8}
        repo_summary = {
            "repository_size_bytes": 4500, "total_files": 25, "files_used": 5, "files_ignored": 20,
            "skills_scanned": 10, "skills_used": 3, "rfcs_used": 2, "specs_used": 1, "engineering_score": 90.0,
            "coverage": {"architecture_coverage": 100.0, "security_coverage": 100.0, "testing_coverage": 100.0, "documentation_coverage": 100.0, "deployment_coverage": 100.0}
        }
        context_summary = {"optimized_size_chars": 2000, "reduction_percentage": 75.0}
        
        res = bench.run_benchmark(token_summary, repo_summary, context_summary)
        self.assertEqual(res["repository_files"], 25)
        self.assertEqual(res["files_used"], 5)
        self.assertEqual(res["estimated_context_reduction_pct"], 75.0)
        self.assertEqual(res["quality_breakdown"]["architecture_quality"], 100.0)

if __name__ == "__main__":
    unittest.main()
