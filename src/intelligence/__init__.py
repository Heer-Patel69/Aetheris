"""
intelligence/__init__.py — Phase 4 exports.

All Phase 4 engines re-exported here so that kernel/core.py and tests can
import from one place.
"""
# Phase 1-3 engines (existing)
from intelligence.cost_analyzer import CostAnalyzer
from intelligence.token_intelligence import TokenIntelligence
from intelligence.repository_metrics import RepositoryMetrics
from intelligence.context_optimizer import ContextOptimizer
from intelligence.historical_analytics import HistoricalAnalytics
from intelligence.dashboard_metrics import DashboardMetrics
from intelligence.benchmark_engine import BenchmarkEngine

# Phase 4 — Model Intelligence
from intelligence.mie import ModelIntelligenceEngine, ModelEntry

# Phase 4 — Prompt Engineering
from intelligence.pce import PromptCompilerEngine, PromptOptimizationEngine
PromptOptimizationEngine  # re-exported for poe.py compatibility

# Phase 4 — Reasoning
from intelligence.ere import (
    EngineeringReasoningEngine,
    SelfReflectionEngine,
    ReasoningMode,
)

# Phase 4 — Verification
from intelligence.fve import FactVerificationEngine, HallucinationDetectionEngine

# Phase 4 — Optimization
from intelligence.optimization_engines import (
    TokenOptimizationEngine,
    CostOptimizationEngine,
    PlanningOptimizationEngine,
    ExecutionOptimizationEngine,
)

# Phase 4 — Orchestration
from intelligence.io import IntelligenceOrchestrator

# Phase 4 — Insights
from intelligence.insights import EngineeringInsightsEngine

__all__ = [
    # Phase 1-3
    "CostAnalyzer", "TokenIntelligence", "RepositoryMetrics",
    "ContextOptimizer", "HistoricalAnalytics", "DashboardMetrics",
    "BenchmarkEngine",
    # Phase 4
    "ModelIntelligenceEngine", "ModelEntry",
    "PromptCompilerEngine", "PromptOptimizationEngine",
    "EngineeringReasoningEngine", "SelfReflectionEngine", "ReasoningMode",
    "FactVerificationEngine", "HallucinationDetectionEngine",
    "TokenOptimizationEngine", "CostOptimizationEngine",
    "PlanningOptimizationEngine", "ExecutionOptimizationEngine",
    "IntelligenceOrchestrator",
    "EngineeringInsightsEngine",
]
