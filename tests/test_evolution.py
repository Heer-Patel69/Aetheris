import unittest
from pathlib import Path
from evolution import (
    SelfEvolutionOrchestrator,
    SelfArchitectureReviewEngine,
    SelfBenchmarkEngine,
    SelfTestingEngine
)

class TestEvolution(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_evolution_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.orchestrator = SelfEvolutionOrchestrator(self.workspace_path)

    def test_architecture_review(self):
        review = SelfArchitectureReviewEngine()
        report = review.review(str(self.workspace_path))
        self.assertEqual(report["flaws_detected"], 0)
        self.assertEqual(report["quality_index"], 98.0)

    def test_benchmark_runs(self):
        bench = SelfBenchmarkEngine()
        res = bench.run_benchmarks()
        self.assertGreater(res["throughput_ops"], 1000)

    def test_regression_testing(self):
        test_engine = SelfTestingEngine()
        res = test_engine.verify_refactored_code()
        self.assertEqual(res["failed"], 0)

    def test_evolution_cycle(self):
        res = self.orchestrator.run_evolution_cycle()
        self.assertEqual(res["status"], "COMPLETED")
        self.assertTrue(res["regression_tests_passed"])
        self.assertEqual(res["release_version"], "3.1.0")
