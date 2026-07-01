import unittest
import os
import shutil
from pathlib import Path
from intelligence.mie import ModelIntelligenceEngine
from intelligence.pce import PromptCompilerEngine
from intelligence.poe import PromptOptimizationEngine
from intelligence.ere import EngineeringReasoningEngine
from intelligence.sre import SelfReflectionEngine
from intelligence.lce import LongContextEngine
from intelligence.kre import KnowledgeRetrievalEngine
from intelligence.mre import MemoryRankingEngine
from intelligence.fve import FactVerificationEngine
from intelligence.hde import HallucinationDetectionEngine
from intelligence.ple import PlanningOptimizationEngine
from intelligence.toe import TokenOptimizationEngine
from intelligence.coe import CostOptimizationEngine
from intelligence.eoe import ExecutionOptimizationEngine
from intelligence.coe2 import ContextOptimizationEngine
from intelligence.dsee import DynamicSkillEvolutionEngine
from intelligence.sbe import SkillBenchmarkEngine
from intelligence.mmce import MultiModelConsensusEngine
from intelligence.io import IntelligenceOrchestrator

class TestRFC004Core(unittest.TestCase):
    def setUp(self):
        self.workspace_dir = Path("c:/AI/Agency owner/aetheris/scratch/test_rfc004")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)
            
    def test_model_intelligence_engine(self):
        mie = ModelIntelligenceEngine(workspace_dir=str(self.workspace_dir))
        self.assertTrue((self.workspace_dir / ".aetheris" / "models" / "model.registry.json").exists())
        self.assertTrue((self.workspace_dir / ".aetheris" / "models" / "model.capabilities.json").exists())
        
        res = mie.get_optimal_model("Test task", 50000)
        self.assertEqual(res["model_id"], "gpt-4o")
        
        res_med = mie.get_optimal_model("Medium context task", 150000)
        self.assertEqual(res_med["model_id"], "claude-3-5-sonnet")
        
        res_large = mie.get_optimal_model("Big context task", 1500000)
        self.assertEqual(res_large["model_id"], "gemini-2.5-pro")

    def test_prompt_compiler_engine(self):
        pce = PromptCompilerEngine()
        res = pce.compile_prompt("code_generation", {"goal": "build auth", "context": "user table exists"})
        self.assertIn("build auth", res["prompt"])

    def test_prompt_optimization_engine(self):
        poe = PromptOptimizationEngine()
        raw_prompt = {"prompt": "  Build auth  \n\n  User table exists  "}
        res = poe.optimize_prompt(raw_prompt)
        self.assertEqual(res["optimized_prompt"], "Build auth\nUser table exists")

    def test_reasoning_and_reflection(self):
        ere = EngineeringReasoningEngine()
        sre = SelfReflectionEngine()
        reasoning = ere.reason_through_problem("Modularize planners", ["Use registry"])
        self.assertEqual(reasoning["confidence"], 0.90)
        reflection = sre.critique_solution(reasoning)
        self.assertEqual(reflection["status"], "APPROVED")

    def test_knowledge_and_context(self):
        lce = LongContextEngine()
        kre = KnowledgeRetrievalEngine()
        mre = MemoryRankingEngine()
        fve = FactVerificationEngine()
        hde = HallucinationDetectionEngine()
        
        self.assertEqual(len(lce.chunk_repository(["file1.py"])), 1)
        self.assertEqual(kre.retrieve_evidence("auth")[0]["source"], "00_SYSTEM_CONSTITUTION.md")
        
        memories = [{"id": 1, "relevance": 0.9, "confidence": 0.8, "freshness": 0.7, "success": 1.0}]
        ranked = mre.rank_memories(memories)
        self.assertTrue(ranked[0]["score"] > 0)
        
        self.assertTrue(fve.verify_fact("EKB holds ASTs")["verified"])
        self.assertEqual(len(hde.scan_for_hallucinations("verified claims")), 0)

    def test_optimization_and_evolution(self):
        ple = PlanningOptimizationEngine()
        toe = TokenOptimizationEngine()
        coe = CostOptimizationEngine()
        eoe = ExecutionOptimizationEngine()
        coe2 = ContextOptimizationEngine()
        dsee = DynamicSkillEvolutionEngine()
        sbe = SkillBenchmarkEngine()
        mmce = MultiModelConsensusEngine()
        intel_io = IntelligenceOrchestrator()
        
        self.assertTrue(ple.optimize_plan({"steps": [1]})["optimized"])
        self.assertEqual(toe.compress_tokens("  hello   world  "), "hello world")
        self.assertTrue(coe.calculate_optimal_cost(1000, "gemini-2.5-flash") > 0)
        self.assertEqual(len(eoe.optimize_execution([1, 2])), 2)
        self.assertEqual(len(coe2.filter_context([{"relevance": 0.8}])), 1)
        self.assertEqual(dsee.evolve_skill("auth", {})["status"], "EVOLVED")
        self.assertEqual(sbe.benchmark_skill("db")["quality_score"], 0.94)
        self.assertEqual(mmce.resolve_consensus([{"ans": 1}])["confidence"], 0.92)
        self.assertEqual(intel_io.assemble_package("refactor")["intelligence_package_status"], "READY")
