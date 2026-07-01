import unittest
import shutil
from pathlib import Path
from learning import LearningSystem, ExperienceMemoryEngine

class TestLearning(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_learning_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.learning = LearningSystem(self.workspace_path)

    def tearDown(self):
        # Clean up files
        shutil.rmtree(self.workspace_path, ignore_errors=True)

    def test_record_experience(self):
        metrics = {"quality_score": 92.0, "latency_seconds": 2.5}
        status = self.learning.process_execution("task-01", "Generate DB schemas", True, metrics=metrics)
        self.assertEqual(status["status"], "PROCESSED")
        self.assertEqual(status["total_runs"], 1)
        self.assertEqual(status["highest_ranked_score"], 92.0)

    def test_pattern_mining(self):
        # Record multiple runs
        self.learning.process_execution("task-01", "Prompt A", True, metrics={"quality_score": 95.0})
        self.learning.process_execution("task-02", "Prompt B", True, metrics={"quality_score": 85.0})
        status = self.learning.process_execution("task-03", "Prompt C", True, metrics={"quality_score": 91.0})
        self.assertEqual(status["patterns_mined"], 2) # Scores > 90
