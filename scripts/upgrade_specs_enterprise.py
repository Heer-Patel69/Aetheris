"""Upgrade Aetheris SPEC markdown files to the enterprise SPEC standard.

This script intentionally generates deterministic documentation from a
hand-maintained architecture catalog plus implementation metadata extracted
from the current Python source tree. It is used to expand the implemented
Aetheris SPEC catalog, including SPEC-001 through SPEC-065 and RFC-006
Learning System SPEC-086 through SPEC-100.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RFC_DIR = ROOT / "rfcs"
UPGRADE_DATE = "2026-07-01"


REQUIRED_HEADINGS = [
    "Executive Summary",
    "Purpose",
    "Goals",
    "Scope",
    "Responsibilities",
    "Design Philosophy",
    "Engineering Principles",
    "Functional Requirements",
    "Non-Functional Requirements",
    "System Context",
    "Internal Architecture",
    "External Architecture",
    "Layer Interactions",
    "Execution Lifecycle",
    "Sequence Of Operations",
    "State Machine",
    "Component Breakdown",
    "Internal Modules",
    "Interfaces",
    "Public APIs",
    "Internal APIs",
    "Data Contracts And JSON Schemas",
    "Configuration And Environment Variables",
    "Generated Artifacts",
    "Input Validation",
    "Output Validation",
    "Failure Modes",
    "Recovery Strategy",
    "Retry Strategy",
    "Logging, Metrics, And Telemetry",
    "Performance Targets",
    "Scalability, Concurrency, And Thread Safety",
    "Memory Management And Caching",
    "Security Considerations",
    "Threat Model And Access Control",
    "Error Handling",
    "Testing Strategy",
    "Unit, Integration, End-To-End, Load, Stress, And Chaos Tests",
    "Dependency Matrix",
    "Traceability Matrix",
    "Risk Assessment",
    "Implementation Guidance",
    "Pseudocode, Examples, And API Definitions",
    "Engineering Guidelines And Anti-Patterns",
    "Known Limitations",
    "Future Evolution",
    "Mermaid Diagrams",
    "PlantUML Diagrams",
    "References",
]


@dataclass(frozen=True)
class SpecRecord:
    number: int
    acronym: str
    name: str
    layer: str
    parent_rfc: str
    scope: str
    source: str
    class_name: str
    description: str


def spec_records() -> list[SpecRecord]:
    """Return the complete implemented Aetheris SPEC architecture catalog."""

    rows = [
        (1, "WDE", "Workspace Discovery Engine", "Engineering Knowledge System", "RFC-001", "Workspace discovery and inventory compilation", "src/intelligence/wde.py", "WorkspaceDiscoveryEngine", "Compiles a deterministic inventory of files, languages, dependencies, frameworks, git metadata, fingerprints, and filesystem graph edges."),
        (2, "URUE", "Universal Requirement Understanding Engine", "Requirement Intelligence", "RFC-001", "Requirement interpretation and normalization", "src/intelligence/urue.py", "UniversalRequirementUnderstandingEngine", "Transforms raw user goals and workspace evidence into normalized business, functional, non-functional, constraint, and acceptance requirement models."),
        (3, "PDE", "Product Discovery Engine", "Product Intelligence", "RFC-001", "Product domain, personas, flows, and complexity discovery", "src/intelligence/pde.py", "ProductDiscoveryEngine", "Merges requirement and workspace evidence into a product plan containing domain classification, personas, user journeys, core flows, and complexity estimates."),
        (4, "APE", "Architecture Planning Engine", "Architecture Intelligence", "RFC-001", "Architecture style, boundaries, storage, and security planning", "src/intelligence/ape.py", "ArchitecturePlanningEngine", "Builds the architecture plan, domain boundaries, storage strategy, security boundaries, module layout, and dependency graph for the product plan."),
        (5, "EDE", "Engineering Decision Engine", "Decision Intelligence", "RFC-001", "Technology decision governance", "src/intelligence/ede.py", "EngineeringDecisionEngine", "Scores alternatives, records weighted architecture and technology decisions, versions decision history, and supports rollback to prior decision states."),
        (6, "EGE", "Engineering Graph Engine", "Graph Intelligence", "RFC-001", "Digital twin dependency graph", "src/intelligence/ege.py", "EngineeringGraphEngine", "Maintains the graph of requirements, modules, tasks, tests, artifacts, and dependencies used for impact analysis and consistency validation."),
        (7, "EKB", "Engineering Knowledge Base", "Knowledge Storage", "RFC-001", "Versioned engineering memory", "src/intelligence/ekb.py", "EngineeringKnowledgeBase", "Persists typed engineering objects with checksums, version history, query filters, integrity checks, and deterministic object identifiers."),
        (8, "QIA", "Query And Impact Analysis Engine", "Query Intelligence", "RFC-001", "Natural-language engineering query and impact traversal", "src/intelligence/qia.py", "QueryAndImpactAnalysisEngine", "Answers engineering questions by resolving query intent and traversing the engineering graph to report impacted nodes and dependent artifacts."),
        (9, "EDPE", "Engineering Design Planning Engine", "Engineering Planning System", "RFC-002", "Design language, UI tokens, and accessibility planning", "src/intelligence/planners.py", "DesignPlanningEngine", "Generates design language tokens, visual style guidance, motion rules, accessibility targets, and reusable view templates."),
        (10, "FPE", "Frontend Planning Engine", "Engineering Planning System", "RFC-002", "Frontend route, page, component, and state planning", "src/intelligence/planners.py", "FrontendPlanningEngine", "Generates frontend routing, application shells, component hierarchy, state context strategy, local caching, and responsive layout expectations."),
        (11, "BPE", "Backend Planning Engine", "Engineering Planning System", "RFC-002", "Backend module, service, controller, and job planning", "src/intelligence/planners.py", "BackendPlanningEngine", "Generates backend bounded modules, service and repository responsibilities, request filters, controllers, background jobs, and operational pipelines."),
        (12, "DPE", "Database Planning Engine", "Engineering Planning System", "RFC-002", "Database schemas, indexes, migrations, backup strategy", "src/intelligence/planners.py", "DatabasePlanningEngine", "Designs the database engine, entity schemas, relationships, indexes, migration sequence, multi-tenancy model, and backup posture."),
        (13, "APIE", "API Planning Engine", "Engineering Planning System", "RFC-002", "API contracts, request schemas, response schemas, and endpoints", "src/intelligence/planners.py", "APIPlanningEngine", "Generates protocol choices, versioning conventions, endpoint contracts, request schemas, response schemas, and rate-limit tiers."),
        (14, "SPE", "Security Planning Engine", "Engineering Planning System", "RFC-002", "Authentication, authorization, threat model, and OWASP planning", "src/intelligence/planners.py", "SecurityPlanningEngine", "Plans authentication standards, authorization matrix, STRIDE threats, OWASP controls, CORS posture, and security headers."),
        (15, "IPE", "Infrastructure Planning Engine", "Engineering Planning System", "RFC-002", "Cloud topology, network, compute, and hosting planning", "src/intelligence/planners.py", "InfrastructurePlanningEngine", "Designs provider selection, region, VPC topology, subnets, compute profile, load-balancer posture, and hosting defaults."),
        (16, "ESPE", "External Services Planning Engine", "Engineering Planning System", "RFC-002", "Vendor integrations and external service contracts", "src/intelligence/planners.py", "ExternalServicesPlanningEngine", "Inventories vendor services, integration contracts, credential boundaries, outbound API dependencies, and service ownership rules."),
        (17, "DPE", "DevOps Planning Engine", "Engineering Planning System", "RFC-002", "CI/CD, branch, container, and deployment planning", "src/intelligence/planners.py", "DevOpsPlanningEngine", "Plans CI/CD stages, branch strategy, container build sequence, release checks, static analysis, and deployment automation."),
        (18, "TPE", "Testing Planning Engine", "Engineering Planning System", "RFC-002", "Test suite architecture and coverage planning", "src/intelligence/planners.py", "TestingPlanningEngine", "Defines unit, integration, smoke, regression, acceptance, security, and performance test suites and the coverage gates they enforce."),
        (19, "DOPE", "Documentation Planning Engine", "Engineering Planning System", "RFC-002", "Runbooks, README, ADR, and API documentation planning", "src/intelligence/planners.py", "DocumentationPlanningEngine", "Outlines documentation artifacts, operating runbooks, ADR requirements, API references, and maintenance ownership."),
        (20, "EEPE", "Engineering Execution Planning Engine", "Engineering Planning System", "RFC-002", "Milestone and sprint execution planning", "src/intelligence/planners.py", "EngineeringExecutionPlanningEngine", "Builds milestone roadmap, sprint dependency order, execution readiness criteria, and delivery planning for the engineering blueprint."),
        (21, "RCPE", "Resource Capacity Planning Engine", "Engineering Planning System", "RFC-002", "Capacity, CPU, RAM, and operational resource planning", "src/intelligence/planners.py", "ResourceCapacityPlanningEngine", "Calculates capacity expectations, resource envelopes, CPU and memory boundaries, and baseline operational sizing."),
        (22, "CPE", "Cost Planning Engine", "Engineering Planning System", "RFC-002", "Cloud, API, and engineering cost planning", "src/intelligence/planners.py", "CostPlanningEngine", "Estimates monthly infrastructure spend, API spend, cost caps, and guardrails for architecture and execution choices."),
        (23, "RPE", "Risk Planning Engine", "Engineering Planning System", "RFC-002", "Technical, security, scalability, and delivery risk planning", "src/intelligence/planners.py", "RiskPlanningEngine", "Identifies risks, mitigation strategies, failure likelihood, impact scores, and production readiness concerns."),
        (24, "CGPE", "Compliance Governance Planning Engine", "Engineering Planning System", "RFC-002", "Compliance and governance planning", "src/intelligence/planners.py", "ComplianceGovernancePlanningEngine", "Plans GDPR, SOC 2, retention, audit trail, access review, and governance control requirements."),
        (25, "OPE", "Observability Planning Engine", "Engineering Planning System", "RFC-002", "Metrics, tracing, logging, and alerting planning", "src/intelligence/planners.py", "ObservabilityPlanningEngine", "Structures application metrics, tracing boundaries, alert thresholds, logs, dashboards, and operational health reporting."),
        (26, "SPPE", "Scalability Performance Planning Engine", "Engineering Planning System", "RFC-002", "Scalability and performance planning", "src/intelligence/planners.py", "ScalabilityPerformancePlanningEngine", "Plans caching, autoscaling, load profile, performance targets, data growth, and horizontal scaling behavior."),
        (27, "DRPE", "Disaster Recovery Planning Engine", "Engineering Planning System", "RFC-002", "Backup, restore, RTO/RPO, and continuity planning", "src/intelligence/planners.py", "DisasterRecoveryPlanningEngine", "Defines RTO, RPO, backup retention, restore routines, continuity checks, failover procedure, and recovery validation."),
        (28, "RRPE", "Release Rollout Planning Engine", "Engineering Planning System", "RFC-002", "Release strategy, canary rollout, and rollback planning", "src/intelligence/planners.py", "ReleaseRolloutPlanningEngine", "Plans release strategy, canary steps, promotion gates, rollback triggers, health checks, and deployment safety thresholds."),
        (29, "MLPE", "Maintenance Lifecycle Planning Engine", "Engineering Planning System", "RFC-002", "Maintenance, lifecycle, and technical debt planning", "src/intelligence/planners.py", "MaintenanceLifecyclePlanningEngine", "Tracks dependency checks, deprecation policy, lifecycle boundaries, technical-debt categories, and maintenance responsibilities."),
        (30, "FEBC", "Final Engineering Blueprint Compiler", "Engineering Planning System", "RFC-002", "Master blueprint compilation and technical design document generation", "src/intelligence/planners.py", "FinalEngineeringBlueprintCompiler", "Compiles validated planning outputs into the authoritative engineering blueprint, KPI report, complexity assessment, execution input, and TDD artifacts."),
        (31, "PVE", "Planning Validation Engine", "Engineering Planning System", "RFC-002", "Cross-planner validation, consistency audit, and blueprint scoring", "src/intelligence/planners.py", "PlanningValidationEngine", "Performs cross-planner validation, theme consistency review, dependency checks, coverage analysis, quality scoring, and warning/failure reporting."),
        (32, "TDE", "Task Decomposition Engine", "Autonomous Engineering Engine", "RFC-003", "Blueprint-to-task decomposition", "src/execution/tde.py", "TaskDecompositionEngine", "Decomposes the engineering blueprint into atomic tasks, modules, stories, subtasks, effort estimates, and execution tree exports."),
        (33, "DGB", "Dependency Graph Builder", "Autonomous Engineering Engine", "RFC-003", "Execution dependency graph and topological scheduling", "src/execution/dgb.py", "DependencyGraphBuilder", "Transforms decomposed tasks into a cycle-free directed graph, topological execution order, critical path, and parallel groups."),
        (34, "SSE", "Skill Selection Engine", "Autonomous Engineering Engine", "RFC-003", "Task-to-skill matching and fallback selection", "src/execution/sse.py", "SkillSelectionEngine", "Matches tasks to specialist skills, ranks skill confidence, identifies missing skill coverage, and recommends fallback execution paths."),
        (35, "MRE", "Model Routing Engine", "Autonomous Engineering Engine", "RFC-003", "Task-specific model routing", "src/execution/mre.py", "ModelRoutingEngine", "Selects execution models according to skill, complexity, latency, quality confidence, provider health, and estimated input/output token cost."),
        (36, "CAE", "Context Assembly Engine", "Autonomous Engineering Engine", "RFC-003", "Execution context packaging", "src/execution/cae.py", "ContextAssemblyEngine", "Retrieves source evidence, dependency references, memory snippets, and task details into bounded context payloads for execution workers."),
        (37, "ES", "Execution Scheduler", "Autonomous Engineering Engine", "RFC-003", "Queue ordering, schedule control, and resource allocation", "src/execution/es.py", "ExecutionScheduler", "Builds execution queues, orders tasks by dependency, allocates schedule steps, handles pause/resume, and reschedules failed work."),
        (38, "PEE", "Parallel Execution Engine", "Autonomous Engineering Engine", "RFC-003", "Parallel task batching and conflict control", "src/execution/pee.py", "ParallelExecutionEngine", "Groups independent tasks into parallel batches, maps file locks, detects conflicts, allocates resources, and supports batch control."),
        (39, "ACGE", "Autonomous Code Generation Engine", "Autonomous Engineering Engine", "RFC-003", "AST-aware code generation and project modification", "src/execution/acge.py", "AutonomousCodeGenerationEngine", "Creates and modifies project files from execution tasks, records implementation decisions, and emits generated-file reports."),
        (40, "SRE", "Self Review Engine", "Autonomous Engineering Engine", "RFC-003", "Generated-code review and quality scoring", "src/execution/sre.py", "SelfReviewEngine", "Reviews generated modifications for style, architecture, security, smells, recommendations, approval, and rejection decisions."),
        (41, "PRE", "Patch Recovery Engine", "Autonomous Engineering Engine", "RFC-003", "Failure classification and patch recovery", "src/execution/pre.py", "PatchRecoveryEngine", "Classifies failures, analyzes root causes, builds patch plans, applies corrections, rolls back unsafe changes, retries, and resumes execution."),
        (42, "SPE", "State Persistence Engine", "Autonomous Engineering Engine", "RFC-003", "Checkpointing and resumable execution state", "src/execution/spe.py", "StatePersistenceEngine", "Serializes checkpoints, snapshots, resume metadata, active task state, and blueprint version for crash-safe execution continuation."),
        (43, "GOE", "Git Operations Engine", "Autonomous Engineering Engine", "RFC-003", "Git branch, commit, tag, rollback, and repository health operations", "src/execution/goe.py", "GitOperationsEngine", "Generates commit plans, branches, tags, merge controls, rollback controls, repository health reports, and traceable commit messages."),
        (44, "DGE", "Documentation Generation Engine", "Autonomous Engineering Engine", "RFC-003", "Documentation generation from engineering logs and decisions", "src/execution/dge.py", "DocumentationGenerationEngine", "Generates README updates, API docs, ADRs, documentation metrics, link validation reports, and decision-history documentation."),
        (45, "EME", "Execution Metrics Engine", "Autonomous Engineering Engine", "RFC-003", "Execution cost, latency, quality, and ROI telemetry", "src/execution/eme.py", "ExecutionMetricsEngine", "Aggregates metrics, dashboards, cost analysis, engineering quality score, performance reports, and historical comparisons."),
        (46, "EO", "Execution Orchestrator", "Autonomous Engineering Engine", "RFC-003", "Central execution runtime orchestration", "src/execution/eo.py", "ExecutionOrchestrator", "Supervises the runtime lifecycle across execution engines, status transitions, cancellation, restart, shutdown, health checks, and orchestration."),
        (47, "MIE", "Model Intelligence Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 1 - Intelligence Core", "src/intelligence/mie.py", "ModelIntelligenceEngine", "Abstracts, registers, benchmarks, and selects the most appropriate language model for task capabilities, context size, cost, and provider constraints."),
        (48, "PCE", "Prompt Compiler Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 1 - Intelligence Core", "src/intelligence/pce.py", "PromptCompilerEngine", "Compiles prompt templates and runtime variables into deterministic prompt packages with goals, constraints, context, and execution metadata."),
        (49, "POE", "Prompt Optimization Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 1 - Intelligence Core", "src/intelligence/poe.py", "PromptOptimizationEngine", "Optimizes compiled prompts by normalizing whitespace, reducing redundant instructions, tightening context, and preserving mandatory constraints."),
        (50, "ERE", "Engineering Reasoning Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 1 - Intelligence Core", "src/intelligence/ere.py", "EngineeringReasoningEngine", "Performs structured engineering reasoning over problems, constraints, alternatives, risks, trade-offs, confidence, and recommended decisions."),
        (51, "SRE", "Self Reflection Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 1 - Intelligence Core", "src/intelligence/sre.py", "SelfReflectionEngine", "Critiques reasoning and solution proposals, verifies consistency against constraints, identifies weaknesses, and approves or rejects candidate outputs."),
        (52, "LCE", "Long Context Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 2 - Knowledge Intelligence", "src/intelligence/lce.py", "LongContextEngine", "Chunks repositories and long input collections into addressable context segments suitable for retrieval, compression, and model-context assembly."),
        (53, "KRE", "Knowledge Retrieval Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 2 - Knowledge Intelligence", "src/intelligence/kre.py", "KnowledgeRetrievalEngine", "Retrieves relevant engineering evidence from RFCs, SPECs, code, tests, documentation, memories, and constitution-level constraints."),
        (54, "MRE", "Memory Ranking Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 2 - Knowledge Intelligence", "src/intelligence/mre.py", "MemoryRankingEngine", "Ranks memory records by relevance, confidence, freshness, success rate, and applicability to the current engineering task."),
        (55, "FVE", "Fact Verification Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 2 - Knowledge Intelligence", "src/intelligence/fve.py", "FactVerificationEngine", "Verifies engineering claims against available evidence and returns confidence, verification status, and claim-level traceability."),
        (56, "HDE", "Hallucination Detection Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 2 - Knowledge Intelligence", "src/intelligence/hde.py", "HallucinationDetectionEngine", "Scans generated text for unsupported claims, unverifiable dependencies, invented APIs, and assertion drift before output is accepted."),
        (57, "PLE", "Planning Optimization Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 3 - Optimization", "src/intelligence/ple.py", "PlanningOptimizationEngine", "Optimizes raw plans by preserving required steps, reducing redundant work, and flagging planning gaps before execution."),
        (58, "TOE", "Token Optimization Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 3 - Optimization", "src/intelligence/toe.py", "TokenOptimizationEngine", "Compresses prompt and context tokens while preserving semantics, constraints, file references, schema names, and required implementation details."),
        (59, "COE", "Cost Optimization Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 3 - Optimization", "src/intelligence/coe.py", "CostOptimizationEngine", "Calculates model and execution cost estimates, compares routing alternatives, and enforces cost-aware recommendations."),
        (60, "EOE", "Execution Optimization Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 3 - Optimization", "src/intelligence/eoe.py", "ExecutionOptimizationEngine", "Optimizes execution task ordering, batching recommendations, and runtime decisions using cost, latency, dependency, and risk signals."),
        (61, "COE2", "Context Optimization Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 3 - Optimization", "src/intelligence/coe2.py", "ContextOptimizationEngine", "Filters context packages by relevance, confidence, freshness, dependency reachability, and available token budget."),
        (62, "DSEE", "Dynamic Skill Evolution Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 4 - Evolution", "src/intelligence/dsee.py", "DynamicSkillEvolutionEngine", "Evolves skill metadata, version recommendations, and improvement signals based on performance metrics and execution feedback."),
        (63, "SBE", "Skill Benchmark Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 4 - Evolution", "src/intelligence/sbe.py", "SkillBenchmarkEngine", "Benchmarks skill quality, reliability, latency, task fit, and production suitability for future routing decisions."),
        (64, "MMCE", "Multi-Model Consensus Engine", "Engineering Intelligence Layer", "RFC-004", "Wave 4 - Evolution", "src/intelligence/mmce.py", "MultiModelConsensusEngine", "Combines candidate model outputs, resolves consensus, estimates confidence, and flags disagreement requiring verification or human review."),
        (65, "IO", "Intelligence Orchestrator", "Engineering Intelligence Layer", "RFC-004", "Wave 4 - Evolution", "src/intelligence/io.py", "IntelligenceOrchestrator", "Coordinates the intelligence pipeline, assembles the final intelligence package, and hands verified guidance to the execution runtime."),
    ]
    rows.extend([
        (66, "PSE", "Plugin SDK Engine", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/sdk/engine.py", "PluginSDKEngine", "Provides the SDK contracts, base interfaces, lifecycle hooks, and validation envelopes required for safe third-party Aetheris extensions."),
        (67, "EME2", "Extension Marketplace Engine", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/marketplace/engine.py", "ExtensionMarketplaceEngine", "Manages extension discovery, trust metadata, publishing workflows, compatibility scoring, and marketplace governance for Aetheris plugins."),
        (68, "RPL", "Runtime Plugin Loader", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/plugin_loader.py", "RuntimePluginLoader", "Loads, validates, isolates, initializes, and unloads runtime plugins without weakening host process safety or contract boundaries."),
        (69, "RPCF", "RPC Framework", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/rpc.py", "RPCFramework", "Provides typed remote procedure calls for distributed runtime components while enforcing authentication, serialization, timeout, and retry policies."),
        (70, "IPCF", "IPC Framework", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/ipc.py", "IPCFramework", "Provides local inter-process communication between runtime components with bounded queues, typed messages, and fail-closed process isolation."),
        (71, "DEE", "Distributed Execution Engine", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/distributed_execution.py", "DistributedExecutionEngine", "Executes validated tasks across distributed workers while preserving dependency ordering, runtime state, telemetry, and recovery semantics."),
        (72, "WPM", "Worker Pool Manager", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/worker_pool.py", "WorkerPoolManager", "Manages local worker capacity, queue assignment, lifecycle state, backpressure, and safe shutdown for concurrent execution workloads."),
        (73, "CLM", "Cluster Manager", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/cluster.py", "ClusterManager", "Coordinates runtime nodes, health, membership, scheduling capacity, and failover boundaries for clustered Aetheris deployments."),
        (74, "NDCR", "Node Discovery Cluster Registry", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/node_registry.py", "NodeDiscoveryClusterRegistry", "Discovers runtime nodes, maintains registry metadata, validates node identity, and publishes cluster topology changes."),
        (75, "DCLE", "Distributed Consensus Leader Election", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/consensus.py", "DistributedConsensusLeaderElection", "Provides consensus and leader election for cluster coordination, exclusive locks, failover decisions, and runtime orchestration ownership."),
        (76, "SEE", "Sandboxed Execution Environment", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/sandbox.py", "SandboxedExecutionEnvironment", "Runs untrusted or high-risk work inside constrained environments with explicit filesystem, network, process, memory, and secret boundaries."),
        (77, "SVSS", "Secure Vault Secrets Service", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/vault.py", "SecureVaultSecretsService", "Stores, retrieves, rotates, and audits runtime secrets without exposing sensitive values to generated artifacts, logs, or model context."),
        (78, "DLEAB", "Distributed Log Event Aggregation Bus", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/log_bus.py", "DistributedLogEventAggregationBus", "Aggregates structured logs and events from runtime nodes into durable streams for observability, incident response, and learning."),
        (79, "HPRMQ", "High Performance Routing Message Queue", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/message_queue.py", "HighPerformanceRoutingMessageQueue", "Routes high-volume runtime messages with priority, backpressure, durability, and latency controls."),
        (80, "RAHS", "Resource Allocator Hardware Scheduler", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/resource_scheduler.py", "ResourceAllocatorHardwareScheduler", "Allocates CPU, memory, disk, network, and accelerator resources according to task priority, capacity, fairness, and safety policy."),
        (81, "DSCS", "Distributed State Cache Synchronization", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/state_cache.py", "DistributedStateCacheSynchronization", "Synchronizes runtime state caches across nodes while preserving consistency, invalidation semantics, and recovery from partial replication."),
        (82, "CITE", "Cryptographic Identity Trust Engine", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/identity_trust.py", "CryptographicIdentityTrustEngine", "Provides cryptographic identity, trust verification, signing, and attestation for runtime nodes, plugins, workers, and messages."),
        (83, "HRLU", "Hot Reload Live Upgrade Subsystem", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/hot_reload.py", "HotReloadLiveUpgradeSubsystem", "Performs safe live upgrades, hot reload, compatibility checks, and rollback coordination for runtime components."),
        (84, "CIFS", "Chaos Injection Fault Simulation Engine", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/runtime/chaos.py", "ChaosInjectionFaultSimulationEngine", "Injects controlled failures to validate runtime resilience, recovery, observability, and production readiness under adverse conditions."),
        (85, "GRO", "Global Runtime Orchestrator", "Runtime Infrastructure Layer", "RFC-005", "Wave 5 - Runtime Infrastructure", "src/execution/orchestrator.py", "GlobalRuntimeOrchestrator", "Coordinates runtime infrastructure across plugins, workers, clusters, queues, secrets, logs, state, identity, upgrades, chaos, and distributed execution."),
        (86, "EME2", "Experience Memory Engine", "Learning System", "RFC-006", "Experience capture, normalization, and replayable learning memory", "src/learning/experience_memory.py", "ExperienceMemoryEngine", "Captures execution experience from logs, metrics, prompts, outputs, failures, user feedback, code changes, and test results so future Aetheris runs can reuse validated historical knowledge."),
        (87, "PME", "Pattern Mining Engine", "Learning System", "RFC-006", "Historical pattern discovery and reusable engineering signal mining", "src/learning/pattern_mining.py", "PatternMiningEngine", "Mines repeated successful and failed execution structures to identify reusable implementation, planning, prompt, architecture, testing, and recovery patterns."),
        (88, "BPE2", "Best Practice Extraction Engine", "Learning System", "RFC-006", "Validated best-practice extraction from historical outcomes", "src/learning/best_practice_extraction.py", "BestPracticeExtractionEngine", "Extracts durable engineering practices from high-confidence success patterns and converts them into reusable guidance for planning, execution, verification, and production operations."),
        (89, "FKE", "Failure Knowledge Engine", "Learning System", "RFC-006", "Failure memory, root-cause capture, and recurrence prevention", "src/learning/failure_knowledge.py", "FailureKnowledgeEngine", "Turns failures, retries, rollbacks, failed tests, and recovery decisions into searchable knowledge that prevents repeated mistakes and improves future recovery choices."),
        (90, "SKE", "Success Knowledge Engine", "Learning System", "RFC-006", "Success memory, quality signal extraction, and reuse ranking", "src/learning/success_knowledge.py", "SuccessKnowledgeEngine", "Captures successful delivery paths, high-quality outputs, passing verification evidence, and low-cost execution strategies for future reuse."),
        (91, "PRE2", "Prompt Refinement Engine", "Learning System", "RFC-006", "Prompt improvement from execution feedback", "src/learning/prompt_refinement.py", "PromptRefinementEngine", "Learns from prompt outcomes, model responses, hallucination findings, review results, and user feedback to refine future prompt templates and prompt assembly rules."),
        (92, "SLE", "Skill Learning Engine", "Learning System", "RFC-006", "Skill performance learning and routing improvement", "src/learning/skill_learning.py", "SkillLearningEngine", "Learns which skills perform well for which task families, captures skill failure modes, and feeds validated performance signals back to skill selection and evolution engines."),
        (93, "ALE", "Architecture Learning Engine", "Learning System", "RFC-006", "Architecture decision learning and pattern reuse", "src/learning/architecture_learning.py", "ArchitectureLearningEngine", "Learns which architecture choices, module boundaries, schemas, and deployment patterns produce reliable and maintainable outcomes across projects."),
        (94, "TLE", "Testing Learning Engine", "Learning System", "RFC-006", "Testing strategy learning and coverage improvement", "src/learning/testing_learning.py", "TestingLearningEngine", "Learns which tests catch defects, which verification gaps recur, and which test templates should be recommended for similar future systems."),
        (95, "RLE", "Recovery Learning Engine", "Learning System", "RFC-006", "Recovery strategy learning and resilience improvement", "src/learning/recovery_learning.py", "RecoveryLearningEngine", "Learns from patch plans, rollback decisions, checkpoint restores, incident records, and recovery outcomes to improve future resilience behavior."),
        (96, "ARSU", "Automatic RFC SPEC Update Engine", "Learning System", "RFC-006", "Controlled documentation update recommendations from validated learning", "src/learning/automatic_rfc_spec_update.py", "AutomaticRFCSpecUpdateEngine", "Converts validated learning into proposed RFC and SPEC updates while preserving governance, traceability, approval, and human-review boundaries."),
        (97, "CLE", "Continuous Learning Engine", "Learning System", "RFC-006", "Continuous learning orchestration and scheduled improvement cycles", "src/learning/continuous_learning.py", "ContinuousLearningEngine", "Runs recurring learning cycles that ingest new experience, validate learning quality, update rankings, publish recommendations, and measure improvement over time."),
        (98, "LAE", "Learning Analytics Engine", "Learning System", "RFC-006", "Learning metrics, dashboards, and effectiveness analysis", "src/learning/learning_analytics.py", "LearningAnalyticsEngine", "Measures whether learning improves quality, cost, reliability, delivery speed, recovery success, prompt quality, skill routing, architecture choices, and production readiness."),
        (99, "AFE", "Adaptive Feedback Engine", "Learning System", "RFC-006", "Feedback ingestion, scoring, and closed-loop adaptation", "src/learning/adaptive_feedback.py", "AdaptiveFeedbackEngine", "Ingests explicit user feedback, implicit execution signals, review comments, production outcomes, and metric deltas to adapt learning recommendations safely."),
        (100, "LSO", "Learning System Orchestrator", "Learning System", "RFC-006", "Learning subsystem coordination and publication pipeline", "src/learning/orchestrator.py", "LearningSystemOrchestrator", "Coordinates SPEC-086 through SPEC-099, manages learning lifecycle state, resolves conflicts between learning signals, and publishes validated recommendations to downstream enterprise and self-evolution systems."),
    ])
    return [SpecRecord(*row) for row in rows]


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return value or "SPEC"


def existing_or_new_path(spec: SpecRecord) -> Path:
    matches = sorted(RFC_DIR.glob(f"SPEC-{spec.number:03d}-*.md"))
    if matches:
        return matches[0]
    return RFC_DIR / f"SPEC-{spec.number:03d}-{sanitize_filename(spec.acronym)}.md"


def unparse_annotation(node: ast.AST | None) -> str:
    if node is None:
        return "Any"
    try:
        return ast.unparse(node)
    except Exception:
        return "Any"


def method_signature(node: ast.FunctionDef) -> str:
    args = []
    for arg in node.args.args:
        if arg.arg == "self":
            continue
        annotation = unparse_annotation(arg.annotation)
        if annotation == "Any":
            args.append(arg.arg)
        else:
            args.append(f"{arg.arg}: {annotation}")
    returns = unparse_annotation(node.returns)
    if returns == "Any":
        returns = "Any"
    return f"{node.name}({', '.join(args)}) -> {returns}"


def collect_metadata(spec: SpecRecord) -> dict[str, Any]:
    source_path = ROOT / spec.source
    metadata: dict[str, Any] = {
        "source_exists": source_path.exists(),
        "source_path": spec.source,
        "classes": [],
        "all_classes": [],
        "methods": [],
        "docstrings": [],
        "artifacts": [],
        "ekb_objects": [],
    }
    if not source_path.exists():
        return metadata

    text = source_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return metadata

    class_nodes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    metadata["all_classes"] = [node.name for node in class_nodes]

    matched: list[ast.ClassDef] = []
    for node in class_nodes:
        doc = ast.get_docstring(node) or ""
        has_spec = f"SPEC-{spec.number:03d}" in doc
        if node.name == spec.class_name or has_spec:
            matched.append(node)

    if spec.number == 30:
        helper_names = {
            "FinalEngineeringBlueprintCompiler",
            "TechnicalDesignDocumentCompiler",
            "PlanningMemoryEngine",
            "BlueprintDiffEngine",
            "ResourceCapacityKPIs",
            "ComplexityAnalyzer",
            "QuestionsEngine",
        }
        matched = [node for node in class_nodes if node.name in helper_names]

    if not matched and class_nodes and spec.source != "src/intelligence/planners.py":
        matched = class_nodes

    segments = []
    for node in matched:
        metadata["classes"].append(node.name)
        doc = ast.get_docstring(node) or ""
        if doc:
            metadata["docstrings"].append(doc)
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                metadata["methods"].append(method_signature(item))
        if hasattr(node, "lineno") and hasattr(node, "end_lineno") and node.end_lineno:
            segments.append("\n".join(lines[node.lineno - 1 : node.end_lineno]))

    segment_text = "\n".join(segments) if segments else text
    artifact_pattern = re.compile(r"[\"']([^\"']+\.(?:json|md|sql|py|yaml|yml|txt))[\"']")
    artifacts = sorted(set(artifact_pattern.findall(segment_text)))
    metadata["artifacts"] = [item for item in artifacts if len(item) < 120]

    ekb_pattern = re.compile(r"register_object\(\s*[\"']([^\"']+)[\"']")
    metadata["ekb_objects"] = sorted(set(ekb_pattern.findall(segment_text)))
    return metadata


def parent_context(spec: SpecRecord) -> str:
    if spec.parent_rfc == "RFC-001":
        return "the Engineering Knowledge Compiler, where evidence is discovered, normalized, stored, and queried before planning begins"
    if spec.parent_rfc == "RFC-002":
        return "the Engineering Planning System, where product, architecture, delivery, operational, and governance plans are compiled before execution"
    if spec.parent_rfc == "RFC-003":
        return "the Autonomous Engineering Engine, where a validated blueprint is decomposed, scheduled, executed, recovered, reviewed, and persisted"
    if spec.parent_rfc == "RFC-005":
        return "the Runtime Infrastructure Layer, where plugins, workers, clusters, queues, secrets, logs, state, identity, upgrades, chaos testing, and distributed execution are coordinated under production safety boundaries"
    if spec.parent_rfc == "RFC-006":
        return "the Learning System, where execution experience is captured, validated, mined, ranked, and converted into safe recommendations that improve future planning, intelligence, execution, recovery, and governance"
    return "the Engineering Intelligence Layer, where prompts, evidence, model choices, reasoning, verification, optimization, and skill evolution are coordinated"


def upstream_downstream(spec: SpecRecord) -> tuple[list[str], list[str]]:
    n = spec.number
    if n == 1:
        return ["User goal, workspace filesystem, git metadata, project manifests"], ["SPEC-002 URUE", "SPEC-003 PDE", "SPEC-007 EKB"]
    if 2 <= n <= 8:
        return [f"SPEC-{n - 1:03d}"], [f"SPEC-{n + 1:03d}" if n < 8 else "SPEC-009 EDPE"]
    if 9 <= n <= 31:
        upstream = ["SPEC-003 PDE", "SPEC-004 APE", "SPEC-007 EKB"]
        if n > 9:
            upstream.append(f"SPEC-{n - 1:03d}")
        downstream = [f"SPEC-{n + 1:03d}" if n < 31 else "SPEC-032 TDE"]
        if n == 30:
            upstream = ["SPEC-012 through SPEC-029", "SPEC-031 PVE", "SPEC-007 EKB"]
            downstream = ["SPEC-032 TDE", "RFC-003 AEE"]
        if n == 31:
            upstream = ["SPEC-012 through SPEC-030", "SPEC-007 EKB"]
            downstream = ["SPEC-030 FEBC", "SPEC-032 TDE"]
        return upstream, downstream
    if 32 <= n <= 46:
        return [f"SPEC-{n - 1:03d}" if n > 32 else "SPEC-030 FEBC"], [f"SPEC-{n + 1:03d}" if n < 46 else "SPEC-045 EME and runtime completion"]
    if 66 <= n <= 85:
        runtime_flow = {
            66: (["SPEC-065 IO", "plugin manifests", "developer SDK contracts"], ["SPEC-067 EME2", "SPEC-068 RPL"]),
            67: (["SPEC-066 PSE", "extension metadata", "trust policies"], ["SPEC-068 RPL"]),
            68: (["SPEC-066 PSE", "SPEC-067 EME2"], ["SPEC-069 RPCF", "SPEC-070 IPCF"]),
            69: (["SPEC-068 RPL", "distributed clients"], ["SPEC-071 DEE", "SPEC-075 DCLE"]),
            70: (["SPEC-068 RPL", "local runtime processes"], ["SPEC-072 WPM", "SPEC-078 DLEAB"]),
            71: (["SPEC-069 RPCF", "SPEC-072 WPM", "SPEC-073 CLM"], ["SPEC-085 GRO"]),
            72: (["SPEC-070 IPCF", "SPEC-080 RAHS"], ["SPEC-071 DEE", "SPEC-085 GRO"]),
            73: (["SPEC-074 NDCR", "SPEC-075 DCLE"], ["SPEC-071 DEE", "SPEC-085 GRO"]),
            74: (["runtime nodes", "cryptographic identities"], ["SPEC-073 CLM", "SPEC-082 CITE"]),
            75: (["SPEC-073 CLM", "SPEC-074 NDCR"], ["SPEC-085 GRO"]),
            76: (["SPEC-077 SVSS", "SPEC-080 RAHS"], ["SPEC-071 DEE", "SPEC-084 CIFS"]),
            77: (["operator secrets", "runtime credentials"], ["SPEC-076 SEE", "SPEC-082 CITE"]),
            78: (["SPEC-070 IPCF", "SPEC-071 DEE", "runtime events"], ["SPEC-045 EME", "SPEC-098 LAE"]),
            79: (["SPEC-069 RPCF", "SPEC-070 IPCF"], ["SPEC-071 DEE", "SPEC-085 GRO"]),
            80: (["worker telemetry", "hardware inventory"], ["SPEC-072 WPM", "SPEC-076 SEE"]),
            81: (["SPEC-073 CLM", "runtime checkpoints"], ["SPEC-085 GRO", "SPEC-095 RLE"]),
            82: (["SPEC-077 SVSS", "node identity records"], ["SPEC-074 NDCR", "SPEC-075 DCLE"]),
            83: (["SPEC-081 DSCS", "release artifacts"], ["SPEC-085 GRO"]),
            84: (["SPEC-076 SEE", "SPEC-083 HRLU"], ["SPEC-095 RLE", "SPEC-098 LAE"]),
            85: (["SPEC-066 through SPEC-084", "SPEC-065 IO"], ["SPEC-086 EME2", "RFC-006 Learning System"]),
        }
        return runtime_flow[n]
    if 86 <= n <= 100:
        learning_flow = {
            86: (["SPEC-045 EME", "SPEC-046 EO", "execution logs", "user feedback"], ["SPEC-087 PME", "SPEC-089 FKE", "SPEC-090 SKE"]),
            87: (["SPEC-086 EME2", "SPEC-007 EKB", "historical artifacts"], ["SPEC-088 BPE2", "SPEC-093 ALE", "SPEC-094 TLE"]),
            88: (["SPEC-087 PME", "SPEC-090 SKE", "SPEC-055 FVE"], ["SPEC-091 PRE2", "SPEC-092 SLE", "SPEC-096 ARSU"]),
            89: (["SPEC-086 EME2", "SPEC-041 PRE", "SPEC-042 SPE"], ["SPEC-095 RLE", "SPEC-098 LAE"]),
            90: (["SPEC-086 EME2", "SPEC-040 SRE", "passing tests"], ["SPEC-088 BPE2", "SPEC-098 LAE"]),
            91: (["SPEC-048 PCE", "SPEC-049 POE", "SPEC-056 HDE", "SPEC-088 BPE2"], ["SPEC-048 PCE", "SPEC-057 PLE"]),
            92: (["SPEC-034 SSE", "SPEC-063 SBE", "SPEC-088 BPE2"], ["SPEC-034 SSE", "SPEC-062 DSEE"]),
            93: (["SPEC-004 APE", "SPEC-087 PME", "SPEC-088 BPE2"], ["SPEC-004 APE", "SPEC-030 FEBC"]),
            94: (["SPEC-018 TPE", "SPEC-040 SRE", "SPEC-087 PME"], ["SPEC-018 TPE", "SPEC-031 PVE"]),
            95: (["SPEC-041 PRE", "SPEC-042 SPE", "SPEC-089 FKE"], ["SPEC-041 PRE", "SPEC-046 EO"]),
            96: (["SPEC-088 BPE2", "SPEC-093 ALE", "SPEC-094 TLE", "SPEC-095 RLE"], ["RFC-006 governance workflow", "ARB review"]),
            97: (["SPEC-086 through SPEC-096"], ["SPEC-098 LAE", "SPEC-100 LSO"]),
            98: (["SPEC-086 through SPEC-097"], ["SPEC-099 AFE", "SPEC-100 LSO"]),
            99: (["SPEC-098 LAE", "user feedback", "production outcomes"], ["SPEC-097 CLE", "SPEC-100 LSO"]),
            100: (["SPEC-086 through SPEC-099"], ["RFC-007 Enterprise", "RFC-008 AI Organization", "RFC-009 Self-Evolution"]),
        }
        return learning_flow[n]
    intelligence_flow = {
        47: (["SPEC-053 KRE", "model.registry.json", "model.capabilities.json"], ["SPEC-050 ERE", "SPEC-035 MRE"]),
        48: (["User goal", "SPEC-001 WDE", "SPEC-002 URUE"], ["SPEC-052 LCE", "SPEC-049 POE"]),
        49: (["SPEC-048 PCE"], ["SPEC-050 ERE", "SPEC-057 PLE"]),
        50: (["SPEC-047 MIE", "SPEC-049 POE", "SPEC-053 KRE"], ["SPEC-055 FVE", "SPEC-051 SRE"]),
        51: (["SPEC-050 ERE", "SPEC-055 FVE", "SPEC-056 HDE"], ["SPEC-057 PLE", "SPEC-065 IO"]),
        52: (["SPEC-048 PCE", "Repository file set"], ["SPEC-053 KRE", "SPEC-061 COE2"]),
        53: (["SPEC-052 LCE", "RFCs", "SPECs", "source code", "tests"], ["SPEC-047 MIE", "SPEC-055 FVE"]),
        54: (["SPEC-007 EKB", "execution history", "decision history"], ["SPEC-053 KRE", "SPEC-057 PLE"]),
        55: (["SPEC-050 ERE", "SPEC-053 KRE"], ["SPEC-056 HDE", "SPEC-051 SRE"]),
        56: (["SPEC-055 FVE", "SPEC-050 ERE"], ["SPEC-051 SRE"]),
        57: (["SPEC-030 FEBC", "SPEC-051 SRE"], ["SPEC-058 TOE", "SPEC-060 EOE"]),
        58: (["SPEC-052 LCE", "SPEC-057 PLE"], ["SPEC-059 COE", "SPEC-061 COE2"]),
        59: (["SPEC-047 MIE", "SPEC-058 TOE"], ["SPEC-060 EOE", "SPEC-035 MRE"]),
        60: (["SPEC-037 ES", "SPEC-059 COE"], ["SPEC-061 COE2", "SPEC-065 IO"]),
        61: (["SPEC-052 LCE", "SPEC-058 TOE", "SPEC-060 EOE"], ["SPEC-062 DSEE", "SPEC-065 IO"]),
        62: (["SPEC-061 COE2", "SPEC-063 SBE"], ["SPEC-064 MMCE", "skill registry updates"]),
        63: (["SPEC-034 SSE", "execution metrics", "skill history"], ["SPEC-062 DSEE", "SPEC-064 MMCE"]),
        64: (["SPEC-047 MIE", "SPEC-050 ERE", "SPEC-063 SBE"], ["SPEC-065 IO", "SPEC-055 FVE"]),
        65: (["SPEC-048 through SPEC-064"], ["RFC-003 AEE", "SPEC-032 TDE"]),
    }
    return intelligence_flow.get(n, ([f"SPEC-{n - 1:03d}"], [f"SPEC-{n + 1:03d}" if n < 65 else "System completion"]))


def test_reference(spec: SpecRecord) -> str:
    if spec.number == 1:
        return "tests/test_wde.py"
    if spec.number == 2:
        return "tests/test_urue.py"
    if spec.number == 3:
        return "tests/test_pde.py"
    if spec.number == 4:
        return "tests/test_ape.py"
    if spec.number == 5:
        return "tests/test_ede.py"
    if spec.number == 6:
        return "tests/test_ege.py"
    if spec.number == 7:
        return "tests/test_ekb.py"
    if spec.number == 8:
        return "tests/test_qia.py"
    if 9 <= spec.number <= 31:
        return "tests/test_planners.py"
    if 32 <= spec.number <= 46:
        return "tests/test_execution.py"
    if 66 <= spec.number <= 85:
        return "tests/plans/runtime-infrastructure-test-plan.md"
    if 86 <= spec.number <= 100:
        return "tests/plans/learning-system-test-plan.md"
    return "tests/test_rfc004_core.py"


def target_latency(spec: SpecRecord) -> str:
    if spec.number == 1:
        return "complete an incremental scan of 10,000 files in less than 30 seconds on developer hardware, excluding intentionally ignored directories"
    if 2 <= spec.number <= 8:
        return "complete core evidence normalization, graph, storage, or query work in less than 2 seconds for a medium workspace"
    if 9 <= spec.number <= 31:
        return "complete a single planner pass in less than 500 milliseconds once upstream product and architecture plans are available"
    if 32 <= spec.number <= 46:
        return "produce execution control artifacts in less than 1 second for a 100-task blueprint, excluding downstream model latency"
    if 66 <= spec.number <= 85:
        return "complete runtime control-plane operations in less than 50 milliseconds excluding network or worker execution latency"
    if 86 <= spec.number <= 100:
        return "complete one learning pass in less than 5 seconds for 10,000 historical events, excluding optional vector index rebuilds"
    return "complete pure-function intelligence operations in less than 100 milliseconds where no model call is required"


def json_block(data: dict[str, Any]) -> str:
    return "```json\n" + json.dumps(data, indent=2) + "\n```"


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered(items: list[str]) -> str:
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, 1))


def section(index: int, title: str, body: str) -> str:
    return f"======================================================================\n{index}. {title.upper()}\n======================================================================\n{body.strip()}\n"


def interface_table(metadata: dict[str, Any], spec: SpecRecord) -> str:
    methods = metadata["methods"] or [f"{spec.class_name}.run(payload: dict) -> dict"]
    rows = ["| API | Purpose | Reliability Contract |", "|---|---|---|"]
    for method in methods:
        method_name = method.split("(", 1)[0]
        rows.append(
            f"| `{method}` | Executes the `{method_name}` responsibility for {spec.acronym}. | Validate input, avoid hidden side effects outside owned artifact paths, return deterministic structured output, and emit traceable failures. |"
        )
    return "\n".join(rows)


def artifacts_text(metadata: dict[str, Any], spec: SpecRecord) -> str:
    artifacts = metadata["artifacts"]
    ekb_objects = metadata["ekb_objects"]
    lines = []
    if artifacts:
        lines.append("Current implementation writes or references these artifacts:")
        lines.append(bullet([f"`{artifact}`" for artifact in artifacts[:24]]))
    else:
        lines.append(
            f"The current `{spec.source}` implementation is primarily in-memory. The enterprise contract still requires {spec.acronym} to expose generated artifacts through the common result envelope and to persist telemetry through the EKB when promoted to production."
        )
    if ekb_objects:
        lines.append("\nEKB object registrations owned by this SPEC:")
        lines.append(bullet([f"`{obj}`" for obj in ekb_objects]))
    else:
        lines.append("\nNo EKB object is currently registered by the source implementation. The production contract must register a typed result object before downstream engines consume the output.")
    return "\n".join(lines)


def schema_examples(spec: SpecRecord, metadata: dict[str, Any]) -> str:
    input_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"{spec.acronym}Input",
        "type": "object",
        "required": ["request_id", "spec_id", "workspace_path", "payload"],
        "properties": {
            "request_id": {"type": "string", "minLength": 8},
            "spec_id": {"const": f"SPEC-{spec.number:03d}"},
            "workspace_path": {"type": "string"},
            "upstream_artifacts": {"type": "array", "items": {"type": "string"}},
            "control_flags": {"type": "object", "additionalProperties": True},
            "payload": {"type": "object", "additionalProperties": True},
        },
    }
    output_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"{spec.acronym}Output",
        "type": "object",
        "required": ["request_id", "spec_id", "status", "artifacts", "telemetry"],
        "properties": {
            "request_id": {"type": "string"},
            "spec_id": {"const": f"SPEC-{spec.number:03d}"},
            "status": {"enum": ["SUCCEEDED", "FAILED", "PARTIAL", "SKIPPED"]},
            "artifacts": {"type": "array", "items": {"type": "string"}},
            "ekb_objects": {"type": "array", "items": {"type": "string"}},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "telemetry": {
                "type": "object",
                "required": ["started_at", "finished_at", "duration_ms"],
                "properties": {
                    "started_at": {"type": "string"},
                    "finished_at": {"type": "string"},
                    "duration_ms": {"type": "number", "minimum": 0},
                    "source_path": {"const": spec.source},
                },
            },
        },
    }
    example = {
        "request_id": f"req-spec-{spec.number:03d}-example",
        "spec_id": f"SPEC-{spec.number:03d}",
        "workspace_path": "<workspace>",
        "upstream_artifacts": upstream_downstream(spec)[0],
        "payload": {
            "engine": spec.name,
            "source_class": spec.class_name,
            "public_methods": metadata["methods"][:5],
        },
    }
    return "\nInput contract:\n" + json_block(input_schema) + "\nOutput contract:\n" + json_block(output_schema) + "\nExample invocation payload:\n" + json_block(example)


def mermaid_diagrams(spec: SpecRecord) -> str:
    upstream, downstream = upstream_downstream(spec)
    up = upstream[0].replace('"', "")
    down = downstream[0].replace('"', "")
    spec_id = f"SPEC-{spec.number:03d}"
    return f"""High-level architecture:
```mermaid
graph TD
    U["{up}"] --> I["Input Validator"]
    I --> E["{spec_id} {spec.acronym}: {spec.name}"]
    E --> C["Contract Validator"]
    C --> A["Owned Artifacts and EKB Objects"]
    A --> D["{down}"]
```

Internal component diagram:
```mermaid
graph LR
    API["Public API"] --> V["Validation Layer"]
    V --> Core["{spec.class_name} Core"]
    Core --> Store["Artifact Writer"]
    Core --> Telemetry["Telemetry Emitter"]
    Store --> EKB["Engineering Knowledge Base"]
```

Sequence diagram:
```mermaid
sequenceDiagram
    participant Upstream as Upstream Engine
    participant Engine as {spec.acronym}
    participant EKB as EKB
    participant Downstream as Downstream Engine
    Upstream->>Engine: Submit {spec_id} input contract
    Engine->>Engine: Validate, execute, and score result
    Engine->>EKB: Persist typed artifacts and telemetry
    Engine-->>Downstream: Emit {spec_id} output contract
```

State machine:
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> ValidatingInput
    ValidatingInput --> Running
    Running --> ValidatingOutput
    ValidatingOutput --> PersistingArtifacts
    PersistingArtifacts --> Completed
    Running --> Recovering
    Recovering --> Running
    Recovering --> Failed
    Failed --> [*]
    Completed --> [*]
```

Data flow diagram:
```mermaid
flowchart LR
    Evidence["Validated Evidence"] --> Payload["{spec.acronym} Payload"]
    Payload --> Transform["Deterministic Transform"]
    Transform --> Result["Structured Result"]
    Result --> Artifacts["Artifacts"]
    Result --> Metrics["Telemetry"]
```

Dependency graph:
```mermaid
graph TD
    Parent["{spec.parent_rfc}"] --> This["{spec_id}"]
    This --> Source["{spec.source}"]
    This --> Test["{test_reference(spec)}"]
    This --> Next["{down}"]
```

Execution pipeline:
```mermaid
graph LR
    A["Load Inputs"] --> B["Validate Contracts"] --> C["Execute {spec.acronym}"] --> D["Persist Artifacts"] --> E["Emit Telemetry"] --> F["Release Downstream"]
```

Error recovery flow:
```mermaid
graph TD
    Error["Failure Detected"] --> Classify["Classify Failure"]
    Classify --> Retry["Retry If Idempotent"]
    Classify --> Fallback["Use Safe Fallback"]
    Retry --> Validate["Revalidate Output"]
    Fallback --> Validate
    Validate --> Done["Resume Pipeline"]
```
"""


def plantuml_diagrams(spec: SpecRecord) -> str:
    upstream, downstream = upstream_downstream(spec)
    up = upstream[0].replace('"', "")
    down = downstream[0].replace('"', "")
    spec_id = f"SPEC-{spec.number:03d}"
    return f"""High-level architecture:
```plantuml
@startuml
rectangle "{up}" as U
rectangle "Input Validator" as V
rectangle "{spec_id} {spec.acronym}" as E
database "EKB / Artifacts" as K
rectangle "{down}" as D
U --> V
V --> E
E --> K
K --> D
@enduml
```

Class diagram:
```plantuml
@startuml
class {spec.class_name} {{
  +execute(input)
  +validate_output(output)
  +emit_telemetry(result)
}}
class "{spec.acronym}InputContract"
class "{spec.acronym}OutputContract"
{spec.class_name} --> "{spec.acronym}InputContract"
{spec.class_name} --> "{spec.acronym}OutputContract"
@enduml
```

Sequence diagram:
```plantuml
@startuml
actor Upstream
participant "{spec.acronym}" as Engine
database "EKB" as EKB
participant Downstream
Upstream -> Engine: submit input contract
Engine -> Engine: validate and execute
Engine -> EKB: persist artifacts
Engine -> Downstream: emit output contract
@enduml
```

State machine:
```plantuml
@startuml
[*] --> Idle
Idle --> ValidatingInput
ValidatingInput --> Running
Running --> ValidatingOutput
ValidatingOutput --> PersistingArtifacts
PersistingArtifacts --> Completed
Running --> Recovering
Recovering --> Running
Recovering --> Failed
Completed --> [*]
Failed --> [*]
@enduml
```

Error recovery flow:
```plantuml
@startuml
start
:Detect failure;
:Classify error;
if (Retryable?) then (yes)
  :Retry with bounded backoff;
else (no)
  :Use fallback or fail closed;
endif
:Validate recovered output;
:Resume downstream pipeline;
stop
@enduml
```
"""


def render_spec(spec: SpecRecord, metadata: dict[str, Any]) -> str:
    spec_id = f"SPEC-{spec.number:03d}"
    upstream, downstream = upstream_downstream(spec)
    source_classes = metadata["classes"] or [spec.class_name]
    internal_classes = metadata["all_classes"][:12] if spec.source != "src/intelligence/planners.py" else source_classes
    if not internal_classes:
        internal_classes = [spec.class_name]
    status = "Frozen" if spec.number == 47 else "Enterprise Standard Draft"
    version = "2.0.0"
    source_note = "validated from source metadata" if metadata["source_exists"] else "source implementation pending"

    intro = f"""# {spec_id}: {spec.name} ({spec.acronym})

Status: {status}
Version: {version}
Parent RFC: {spec.parent_rfc}
Layer: {spec.layer}
Scope: {spec.scope}
Canonical Standard: SPEC-047 Enterprise Standard
Upgrade Date: {UPGRADE_DATE}
Implementation: `{spec.source}` ({source_note})
Primary Class: `{spec.class_name}`
Test Reference: `{test_reference(spec)}`
"""

    sections: list[str] = []
    sections.append(section(1, "Executive Summary", f"""{spec.name} exists to make {spec.layer} deterministic, reviewable, and safe at production scale. {spec.description}

This document upgrades {spec_id} from a lightweight subsystem note into an enterprise engineering specification. It defines why the engine exists, how it operates internally, which contracts it owns, how it interacts with neighboring engines, how it fails, how it recovers, how engineers should test it, and how future changes should preserve compatibility with the Aetheris constitution.

{spec_id} is part of {parent_context(spec)}."""))

    sections.append(section(2, "Purpose", f"""The purpose of {spec.acronym} is to own the full engineering responsibility for {spec.scope.lower()}. It converts upstream evidence into a downstream-safe contract without asking later engines to infer missing details.

The engine is necessary because Aetheris is an Autonomous Software Engineering Operating System, not a best-effort prompt chain. Each engine must own one bounded transformation, produce typed evidence, record what it decided, and allow downstream engines to continue without reinterpreting raw context.

Alternatives rejected:
- Embedding {spec.acronym} behavior into a general orchestrator was rejected because it hides ownership and makes failures hard to isolate.
- Letting downstream engines reconstruct {spec.scope.lower()} was rejected because it duplicates logic and creates inconsistent plans.
- Relying on unstructured markdown output was rejected because execution, recovery, validation, and telemetry require machine-readable contracts."""))

    sections.append(section(3, "Goals", bullet([
        f"Provide a deterministic implementation contract for {spec.scope.lower()}.",
        f"Accept only validated upstream artifacts from {', '.join(upstream)}.",
        f"Emit structured output that can be consumed by {', '.join(downstream)}.",
        "Record artifacts and telemetry so decisions are inspectable after execution.",
        "Fail closed when required evidence is missing, malformed, stale, or contradictory.",
        "Keep implementation behavior aligned with the Aetheris constitution, RFC boundaries, and SPEC-047 enterprise standard.",
        "Support incremental improvement without breaking public contracts or historical artifacts.",
    ])))

    sections.append(section(4, "Scope", f"""In scope:
{bullet([
        spec.scope,
        f"Validation of all {spec.acronym} input and output structures.",
        "Artifact generation, EKB registration, telemetry emission, and downstream handoff.",
        "Recovery behavior for missing inputs, invalid contracts, stale cache, and partial execution.",
        "Operational guidance for tests, observability, security, performance, and future evolution.",
    ])}

Out of scope:
{bullet([
        "Owning responsibilities assigned to upstream or downstream SPECs.",
        "Executing arbitrary user project code unless another SPEC explicitly grants that responsibility.",
        "Persisting secrets, API keys, or opaque model credentials in generated artifacts.",
        "Silently fabricating missing evidence or architecture conclusions.",
    ])}"""))

    sections.append(section(5, "Responsibilities", bullet([
        f"Own the transformation from `{spec_id}` input contract to `{spec_id}` output contract.",
        f"Use `{spec.source}` as the implementation boundary and `{spec.class_name}` as the primary class boundary.",
        "Validate all required upstream evidence before starting irreversible work.",
        "Generate typed artifacts only in the engine-owned output directories or documented EKB objects.",
        "Emit structured errors that allow PRE, SPE, EME, and IO to classify, persist, recover, or report the failure.",
        "Maintain backward-compatible public APIs unless the parent RFC version is advanced.",
        "Expose enough traceability for a senior engineer to audit decisions without reverse-engineering the code.",
    ])))

    sections.append(section(6, "Design Philosophy", f"""{spec.acronym} follows the Aetheris principle: think more, generate less, reuse whenever possible. The engine should perform the minimum deterministic transformation that completely satisfies its contract and should reuse upstream artifacts instead of rescanning or re-deriving evidence.

The design is intentionally layered:
- Upstream engines provide evidence.
- {spec.acronym} validates and transforms that evidence.
- EKB and artifact storage preserve the result.
- Downstream engines consume only the validated contract.

This design makes the engine independently testable and allows failures to be traced to a specific SPEC boundary."""))

    sections.append(section(7, "Engineering Principles", bullet([
        "Determinism: identical validated inputs must produce equivalent outputs except for timestamps and run identifiers.",
        "Evidence-first operation: conclusions must reference upstream artifacts, source files, tests, or recorded EKB objects.",
        "Single responsibility: the engine must not absorb neighboring SPEC behavior for convenience.",
        "Typed boundaries: public APIs must accept and return structured payloads.",
        "Idempotent persistence: rerunning the same request should not corrupt historical artifacts.",
        "Fail-closed security: missing authorization, secrets, or unknown file paths must halt the unsafe branch.",
        "Observability by default: every run must be measurable and explainable.",
        "Recovery readiness: failures must include enough information to retry, roll back, or continue safely.",
    ])))

    sections.append(section(8, "Functional Requirements", bullet([
        f"FR-001: {spec.acronym} shall load the upstream artifacts declared by {', '.join(upstream)}.",
        f"FR-002: {spec.acronym} shall validate `request_id`, `workspace_path`, `spec_id`, and payload shape before execution.",
        f"FR-003: {spec.acronym} shall execute the primary behavior owned by `{spec.class_name}`.",
        f"FR-004: {spec.acronym} shall emit an output contract containing status, artifacts, EKB object identifiers, warnings, and telemetry.",
        "FR-005: The engine shall distinguish hard failures from partial completion and skipped work.",
        "FR-006: The engine shall preserve upstream traceability in every generated result.",
        "FR-007: The engine shall expose stable public APIs for orchestrator use.",
        "FR-008: The engine shall be safe to rerun after a crash or interrupted execution.",
    ])))

    sections.append(section(9, "Non-Functional Requirements", bullet([
        f"Latency target: {target_latency(spec)}.",
        "Reliability target: no unhandled exception should leave partially written artifacts without an error record.",
        "Compatibility target: output contracts must remain backward compatible for minor version upgrades.",
        "Security target: no secret value may be written to markdown, JSON, logs, telemetry, or EKB records.",
        "Scalability target: processing must scale with relevant input size, not with the entire repository when cached evidence exists.",
        "Maintainability target: implementation must remain readable, modular, and testable by a senior engineer in isolation.",
        "Auditability target: every material decision must be explainable through input evidence or deterministic rules.",
    ])))

    sections.append(section(10, "System Context", f"""{spec_id} sits in `{spec.layer}` under `{spec.parent_rfc}`. It is not an isolated utility; it is one stage in the Aetheris operating-system pipeline.

Upstream dependencies:
{bullet(upstream)}

Downstream consumers:
{bullet(downstream)}

The engine must treat upstream data as evidence, not truth. It must validate structure and consistency before use. Downstream engines must treat {spec.acronym} output as the authoritative contract for {spec.scope.lower()} unless a later validation SPEC rejects it."""))

    sections.append(section(11, "Internal Architecture", f"""Primary implementation path: `{spec.source}`.

Primary implementation class: `{spec.class_name}`.

Implementation classes in scope:
{bullet([f"`{cls}`" for cls in internal_classes])}

Core architecture:
- Public API boundary accepts the invocation payload.
- Validation layer checks identity, required upstream artifacts, and payload shape.
- Core transformation layer performs the domain-specific work described by this SPEC.
- Persistence layer writes artifacts and EKB records.
- Telemetry layer emits timing, status, warnings, and error classification.
- Downstream handoff layer returns the typed output contract."""))

    sections.append(section(12, "External Architecture", f"""{spec.acronym} is invoked by the Aetheris kernel, an orchestrator, or a parent pipeline runner. It should not require callers to know implementation internals.

External callers see:
- Stable input schema.
- Stable output schema.
- Public methods listed in this document.
- Typed exceptions or failure objects.
- Generated artifacts in known directories.

External callers must not depend on private helper classes, internal cache format, temporary file names, or incidental implementation details."""))

    sections.append(section(13, "Layer Interactions", f"""Layer interactions are governed by the parent RFC boundary:
- `{spec.parent_rfc}` owns why this engine exists.
- `{spec_id}` owns how the engine is implemented.
- `SPEC-007 EKB` owns durable typed memory when EKB records are registered.
- `SPEC-045 EME` owns aggregate execution metrics.
- `SPEC-041 PRE` owns patch recovery when implementation errors are recoverable.
- `SPEC-042 SPE` owns resumable state when the run is interrupted.

{spec.acronym} must exchange data by contract, not by implicit global state."""))

    sections.append(section(14, "Execution Lifecycle", numbered([
        "Receive invocation payload from upstream pipeline or orchestrator.",
        "Validate request identity, spec identity, workspace path, control flags, and payload shape.",
        "Resolve upstream artifact references and confirm they are readable within the workspace boundary.",
        f"Execute `{spec.class_name}` behavior for {spec.scope.lower()}.",
        "Validate the produced output contract and generated artifacts.",
        "Persist artifacts, EKB objects, and telemetry.",
        "Return structured success, partial success, skipped, or failed status to downstream consumers.",
    ])))

    sections.append(section(15, "Sequence Of Operations", f"""Canonical sequence:
{numbered([
        f"Load upstream dependencies: {', '.join(upstream)}.",
        "Normalize input payload into the internal domain model.",
        "Reject missing, stale, or contradictory evidence before executing core behavior.",
        f"Run the {spec.acronym} core transformation.",
        "Generate artifacts and EKB records.",
        "Validate output against the JSON schema in this SPEC.",
        f"Release the output to {', '.join(downstream)}.",
    ])}"""))

    sections.append(section(16, "State Machine", bullet([
        "`Idle`: No active invocation is being processed.",
        "`ValidatingInput`: Contract, workspace path, upstream artifact, and payload checks are running.",
        "`Running`: Core transformation is active.",
        "`ValidatingOutput`: Generated result is checked against schema and downstream expectations.",
        "`PersistingArtifacts`: Output files, telemetry, and EKB records are written atomically where possible.",
        "`Completed`: Output is released to downstream engines.",
        "`Recovering`: Retry or fallback behavior is active after a known failure mode.",
        "`Failed`: No valid output can be released and downstream execution must halt or route to recovery.",
    ])))

    sections.append(section(17, "Component Breakdown", bullet([
        "`InputContract`: Captures request identity, workspace path, upstream artifacts, control flags, and payload.",
        "`InputValidator`: Enforces schema, workspace boundary, and required dependency checks.",
        f"`{spec.class_name}`: Owns the core {spec.scope.lower()} behavior.",
        "`ArtifactWriter`: Persists JSON, markdown, graph, report, checkpoint, or plan artifacts.",
        "`EKBAdapter`: Registers typed objects and preserves traceability when the engine owns durable knowledge.",
        "`TelemetryEmitter`: Records duration, status, warnings, errors, and downstream handoff metadata.",
        "`OutputValidator`: Verifies schema, required artifact references, and status semantics before release.",
    ])))

    sections.append(section(18, "Internal Modules", f"""Internal modules and helper classes should stay private unless explicitly listed as public APIs.

Detected implementation classes:
{bullet([f"`{cls}`" for cls in internal_classes])}

Detected class docstrings:
{bullet([item for item in metadata["docstrings"][:8]] or [spec.description])}

Engineers extending this SPEC should prefer adding small helper classes under the same module boundary before introducing cross-layer dependencies."""))

    sections.append(section(19, "Interfaces", f"""Interface boundaries:
- Input interface: `{spec.acronym}Input` JSON object.
- Output interface: `{spec.acronym}Output` JSON object.
- Source interface: `{spec.source}`.
- Public class boundary: `{spec.class_name}`.
- EKB interface: `EngineeringKnowledgeBase.register_object`, `get_object`, and `query_objects` when persistent memory is required.
- Telemetry interface: event records and metrics consumed by `SPEC-045 EME`.

Interfaces must be stable, documented, and covered by tests before downstream SPECs depend on them."""))

    sections.append(section(20, "Public APIs", interface_table(metadata, spec)))

    sections.append(section(21, "Internal APIs", f"""Internal APIs include private helper methods, local validators, cache utilities, and artifact writers. They may change between patch versions when public contracts remain stable.

Internal API rules:
{bullet([
        "Prefix non-public helpers with an underscore or keep them module-local.",
        "Do not expose raw file handles, mutable global state, or unvalidated dictionaries to downstream engines.",
        "Return structured data from helpers so tests can assert behavior without reading files when practical.",
        "Keep helper methods deterministic and side-effect free unless they explicitly belong to the persistence layer.",
    ])}"""))

    sections.append(section(22, "Data Contracts And JSON Schemas", schema_examples(spec, metadata)))

    sections.append(section(23, "Configuration And Environment Variables", f"""Configuration sources:
- Repository defaults under `aetheris/config/` when applicable.
- Workspace-scoped state under `.aetheris/`.
- Runtime override flags in the invocation payload.
- Environment variables only for documented path, feature, or provider overrides.

Recommended environment variables:
{bullet([
        f"`AETHERIS_{spec.acronym}_ENABLED`: Optional feature gate for this engine.",
        f"`AETHERIS_{spec.acronym}_STRICT`: When true, converts warnings to failures for CI or release validation.",
        f"`AETHERIS_{spec.acronym}_OUTPUT_DIR`: Optional override for generated artifacts during tests.",
    ])}

Secrets must never be supplied through generated SPEC artifacts. Provider tokens, credentials, and private keys must remain in the platform secret store or caller environment and must be redacted from telemetry."""))

    sections.append(section(24, "Generated Artifacts", artifacts_text(metadata, spec)))

    sections.append(section(25, "Input Validation", bullet([
        "`spec_id` must equal the current SPEC identifier.",
        "`request_id` must be present, unique for the execution attempt, and safe for logs.",
        "`workspace_path` must resolve inside the active Aetheris workspace or an explicitly allowed test workspace.",
        "All upstream artifact references must exist, be readable, and match expected JSON or markdown structure.",
        "Payload dictionaries must contain only supported keys unless the schema explicitly allows extension fields.",
        "Control flags must be typed and must not disable mandatory safety, validation, telemetry, or security checks.",
        "Input data containing secrets must be rejected or redacted before persistence.",
    ])))

    sections.append(section(26, "Output Validation", bullet([
        "Output must include status, artifacts, EKB object identifiers, warnings, and telemetry.",
        "Artifacts listed in the output must exist or be marked as intentionally in-memory.",
        "Failed outputs must include classification, message, retryability, and recovery guidance.",
        "Partial outputs must identify which required artifacts are missing and which downstream engines are blocked.",
        "EKB object identifiers must resolve successfully after registration.",
        "Telemetry duration must be non-negative and status must match the output status.",
    ])))

    sections.append(section(27, "Failure Modes", bullet([
        "Missing upstream artifact or empty required input.",
        "Malformed JSON, markdown, graph, or schema payload.",
        "Workspace path violation or unreadable file due to permissions.",
        "Conflicting evidence between upstream plans, EKB records, and current workspace state.",
        "Output artifact write failure, partial write, or checksum mismatch.",
        "Unexpected implementation exception inside the primary class.",
        "Telemetry sink unavailable or EKB registration failure.",
        "Downstream contract incompatibility after a version change.",
    ])))

    sections.append(section(28, "Recovery Strategy", f"""Recovery is conservative. {spec.acronym} may retry idempotent reads, regenerate deterministic artifacts, or fall back to a documented safe default. It must not fabricate architecture, code, security, cost, or evidence decisions to hide missing data.

Recovery actions:
{bullet([
        "Re-read upstream artifacts once when the first read fails because of a transient filesystem condition.",
        "Regenerate deterministic output artifacts from validated inputs when prior files are missing or corrupt.",
        "Register a failure object in EKB when recovery cannot produce a safe output.",
        "Delegate patchable implementation errors to SPEC-041 PRE.",
        "Delegate interrupted runs to SPEC-042 SPE when checkpoint state is available.",
        "Fail closed when secrets, path traversal, or evidence fabrication risk is detected.",
    ])}"""))

    sections.append(section(29, "Retry Strategy", bullet([
        "Use bounded retries only for idempotent reads, writes, and registry lookups.",
        "Do not retry semantic validation failures; return a structured error that explains the missing or invalid evidence.",
        "Use exponential backoff for external provider checks when this SPEC is extended to call external services.",
        "Stop retrying after the configured retry budget and emit a recoverable or terminal failure classification.",
        "Preserve the original request ID and attach a retry counter to telemetry.",
    ])))

    sections.append(section(30, "Logging, Metrics, And Telemetry", f"""Required telemetry:
{bullet([
        f"`{spec.acronym}_STARTED` with request ID, spec ID, source path, and upstream references.",
        f"`{spec.acronym}_COMPLETED` with status, duration, artifact count, EKB object count, and warning count.",
        f"`{spec.acronym}_FAILED` with failure class, retryability, and recovery guidance.",
        "Per-run duration in milliseconds.",
        "Input size and output size where measurable.",
        "Validation failure counts grouped by schema, artifact, security, and consistency categories.",
    ])}

Logs must be structured JSON, redact secrets, and avoid dumping full prompt, code, or model payloads unless an explicit debug mode is enabled."""))

    sections.append(section(31, "Performance Targets", bullet([
        f"Primary latency target: {target_latency(spec)}.",
        "Output validation should add less than 10 percent overhead to the core transformation.",
        "Artifact persistence should be batched where possible to reduce filesystem churn.",
        "Large inputs should be processed incrementally or from existing EKB evidence instead of repeatedly scanning the workspace.",
        "Performance regressions greater than 20 percent require a benchmark note and mitigation plan.",
    ])))

    sections.append(section(32, "Scalability, Concurrency, And Thread Safety", f"""Scalability model:
- {spec.acronym} must scale by consuming scoped upstream artifacts rather than global mutable state.
- Repeated invocations must be safe when they operate on different request IDs.
- Concurrent writes to the same artifact path must use deterministic overwrite, atomic write, or caller-provided execution locks.
- EKB registration must be versioned so concurrent runs do not erase history.

Thread safety:
- Pure transformations should be stateless.
- Mutable instance fields must represent run-local state or be protected by caller-level execution scheduling.
- Shared registries, caches, and output files must be safe under parallel execution controlled by SPEC-038 PEE."""))

    sections.append(section(33, "Memory Management And Caching", bullet([
        "Prefer streaming or bounded in-memory structures for large artifact reads.",
        "Cache only deterministic intermediate data that can be invalidated by file fingerprint, request ID, or upstream artifact version.",
        "Never cache secrets, raw credentials, or unredacted provider responses.",
        "Release large context payloads after output validation when downstream consumers only need artifact references.",
        "Use EKB versions as durable cache keys when results must survive across sessions.",
    ])))

    sections.append(section(34, "Security Considerations", f"""{spec.acronym} is inside the Aetheris trust boundary but must still defend against unsafe project content, prompt injection embedded in source files, path traversal, malformed schemas, and poisoned upstream artifacts.

Security controls:
{bullet([
        "Resolve paths before reading or writing and enforce workspace boundaries.",
        "Treat repository text as untrusted evidence until validated by source, schema, and context.",
        "Redact secrets before logs, telemetry, markdown, JSON, and EKB records are written.",
        "Apply least privilege: this SPEC may only write artifacts it owns.",
        "Fail closed on unknown control flags that attempt to bypass validation or security checks.",
    ])}"""))

    sections.append(section(35, "Threat Model And Access Control", bullet([
        "Threat: Malicious workspace file attempts path traversal through an artifact reference. Control: canonical path resolution and workspace-bound writes.",
        "Threat: Prompt-injection text inside code or docs asks the engine to ignore SPEC constraints. Control: treat text as data and enforce this SPEC over file instructions.",
        "Threat: Stale EKB record contradicts current source. Control: compare source fingerprints or upstream artifact versions before trusting the record.",
        "Threat: Unauthorized caller invokes the engine with a forged workspace path. Control: orchestrator-level authorization and local path policy validation.",
        "Threat: Downstream engine consumes partial output as complete. Control: strict status and missing-artifact semantics in the output schema.",
    ])))

    sections.append(section(36, "Error Handling", f"""Errors must be explicit and typed. {spec.acronym} should prefer structured failure returns over unhandled exceptions once an invocation context exists.

Error categories:
{bullet([
        "`INPUT_SCHEMA_ERROR`: required input field missing or malformed.",
        "`UPSTREAM_ARTIFACT_ERROR`: dependency missing, unreadable, stale, or contradictory.",
        "`SECURITY_POLICY_ERROR`: path, secret, injection, or access-control violation.",
        "`TRANSFORMATION_ERROR`: primary class failed while executing core behavior.",
        "`OUTPUT_SCHEMA_ERROR`: generated result does not satisfy the contract.",
        "`PERSISTENCE_ERROR`: artifact, telemetry, or EKB write failed.",
    ])}"""))

    sections.append(section(37, "Testing Strategy", f"""Primary test reference: `{test_reference(spec)}`.

Testing must cover:
{bullet([
        "Happy-path transformation with representative upstream artifacts.",
        "Missing input, malformed input, and contradictory input failures.",
        "Generated artifact presence and schema validity.",
        "EKB object registration and retrieval when this SPEC owns memory.",
        "Telemetry status and duration fields.",
        "Idempotent rerun behavior.",
        "Downstream handoff compatibility.",
    ])}"""))

    sections.append(section(38, "Unit, Integration, End-To-End, Load, Stress, And Chaos Tests", bullet([
        f"Unit tests should instantiate `{spec.class_name}` directly and verify public method behavior.",
        "Integration tests should execute the upstream and downstream SPEC pair around this engine.",
        "End-to-end tests should run the parent RFC pipeline through this SPEC and validate final artifacts.",
        "Load tests should scale representative input sizes until latency, memory, or artifact size budgets are reached.",
        "Stress tests should simulate missing files, corrupted JSON, partial writes, and large context payloads.",
        "Chaos tests should interrupt execution between validation, transformation, persistence, and downstream handoff, then verify resumability or clean failure.",
    ])))

    dependency_rows = [
        "| Dependency | Relationship | Contract |",
        "|---|---|---|",
        *[f"| `{item}` | Upstream | Must provide validated evidence before {spec.acronym} starts. |" for item in upstream],
        *[f"| `{item}` | Downstream | Must consume only the validated {spec.acronym} output contract. |" for item in downstream],
        f"| `{spec.source}` | Implementation | Must remain aligned with this SPEC. |",
        f"| `{test_reference(spec)}` | Verification | Must cover the behavior and artifact contract. |",
    ]
    sections.append(section(39, "Dependency Matrix", "\n".join(dependency_rows)))

    trace_rows = [
        "| Requirement | Verification Evidence |",
        "|---|---|",
        f"| FR-001 upstream loading | `{test_reference(spec)}` fixtures and upstream artifact validation |",
        f"| FR-002 input validation | Schema tests and malformed payload cases |",
        f"| FR-003 core execution | Direct `{spec.class_name}` public API tests |",
        "| FR-004 output contract | JSON schema validation and artifact existence checks |",
        "| FR-005 failure semantics | Negative tests for missing, malformed, and conflicting inputs |",
        "| FR-006 traceability | EKB objects, telemetry records, and artifact references |",
        "| FR-007 public API stability | Backward-compatible method signature and contract tests |",
        "| FR-008 rerun safety | Idempotent rerun and recovery tests |",
    ]
    sections.append(section(40, "Traceability Matrix", "\n".join(trace_rows)))

    sections.append(section(41, "Risk Assessment", bullet([
        f"Risk: {spec.acronym} grows beyond its single responsibility. Mitigation: reject cross-SPEC behavior and keep responsibilities explicit.",
        "Risk: generated artifacts drift from implementation. Mitigation: validate against source-derived metadata and tests.",
        "Risk: downstream engines consume stale or partial outputs. Mitigation: strict status semantics and schema validation.",
        "Risk: hidden prompt injection or poisoned repository content influences decisions. Mitigation: evidence validation and SPEC precedence.",
        "Risk: duplicate acronyms across planning and execution specs confuse routing. Mitigation: always route by `SPEC-XXX` first and acronym second.",
        "Risk: missing tests allow contract drift. Mitigation: update the referenced test suite whenever public APIs or artifacts change.",
    ])))

    sections.append(section(42, "Implementation Guidance", f"""Recommended package structure:
```text
{spec.source}
tests/{Path(test_reference(spec)).name}
.aetheris/<engine-owned-output>/
rfcs/{existing_or_new_path(spec).name}
```

Guidance:
{bullet([
        f"Keep `{spec.class_name}` as the primary orchestration class for this SPEC.",
        "Add validators before adding new transformation behavior.",
        "Add typed output fields before downstream engines need them.",
        "Keep source-level comments concise and use this SPEC for architecture explanation.",
        "Prefer standard library parsers and structured JSON over ad hoc string parsing.",
        "Update tests, schemas, artifacts, and this SPEC in the same change when contracts evolve.",
    ])}"""))

    methods_for_pseudo = metadata["methods"][:3] or [f"{spec.class_name}.execute(payload: dict) -> dict"]
    sections.append(section(43, "Pseudocode, Examples, And API Definitions", f"""Example pseudocode:
```python
def run_{spec.acronym.lower()}(payload: dict) -> dict:
    input_contract = validate_{spec.acronym.lower()}_input(payload)
    upstream = load_upstream_artifacts(input_contract["upstream_artifacts"])
    result = {spec.class_name}(workspace_path=input_contract["workspace_path"]).execute(upstream)
    output = build_{spec.acronym.lower()}_output(input_contract, result)
    validate_{spec.acronym.lower()}_output(output)
    persist_artifacts(output)
    emit_telemetry(output)
    return output
```

Public API definitions:
{bullet([f"`{method}`" for method in methods_for_pseudo])}

Example output:
{json_block({
        "request_id": f"req-spec-{spec.number:03d}-example",
        "spec_id": spec_id,
        "status": "SUCCEEDED",
        "artifacts": metadata["artifacts"][:5],
        "ekb_objects": metadata["ekb_objects"][:5],
        "warnings": [],
        "telemetry": {
            "source_path": spec.source,
            "duration_ms": 12.5,
        },
    })}"""))

    sections.append(section(44, "Engineering Guidelines And Anti-Patterns", f"""Guidelines:
{bullet([
        "Keep every decision tied to evidence.",
        "Prefer smaller deterministic helpers over opaque orchestration blocks.",
        "Use exact SPEC IDs in logs, artifacts, and telemetry.",
        "Version any contract that downstream engines persist or replay.",
        "Document intentional trade-offs in this SPEC before encoding them in code.",
    ])}

Anti-patterns:
{bullet([
        "Do not skip validation because an upstream engine is expected to be correct.",
        "Do not write artifacts outside the workspace or engine-owned directories.",
        "Do not treat markdown prose as a substitute for JSON contracts.",
        "Do not hide failures by returning empty success objects.",
        "Do not introduce network or model calls into a synchronous path without budget, retry, and timeout controls.",
        "Do not duplicate logic already owned by another SPEC.",
    ])}"""))

    sections.append(section(45, "Known Limitations", bullet([
        "The current implementation may be thinner than this enterprise contract; this SPEC defines the production target and upgrade path.",
        "Some planner engines are currently implemented inside `src/intelligence/planners.py`; future decomposition should preserve public contracts while moving classes into dedicated modules.",
        "Some intelligence engines are pure-function prototypes; production promotion requires telemetry, persistence, and richer validation.",
        "Current tests emphasize deterministic examples; broader load, stress, and chaos coverage should be added as the engine matures.",
        "External provider behavior, model latency, and secret storage are outside this SPEC unless explicitly described in the source implementation.",
    ])))

    sections.append(section(46, "Future Evolution", bullet([
        "Split monolithic modules into per-SPEC packages when module size or ownership boundaries justify the change.",
        "Promote JSON schemas into reusable files under `aetheris/schemas/` once the contract stabilizes.",
        "Add benchmark fixtures and historical performance baselines.",
        "Integrate telemetry with dashboards generated by SPEC-045 EME.",
        "Add recovery drills that intentionally corrupt artifacts and verify deterministic regeneration.",
        "Expand traceability links between RFCs, SPECs, source files, tests, and generated runtime artifacts.",
    ])))

    sections.append(section(47, "Mermaid Diagrams", mermaid_diagrams(spec)))
    sections.append(section(48, "PlantUML Diagrams", plantuml_diagrams(spec)))
    sections.append(section(49, "References", bullet([
        "`00_SYSTEM_CONSTITUTION.md`",
        f"`rfcs/{spec.parent_rfc}`",
        f"`{spec.source}`",
        f"`{test_reference(spec)}`",
        "`rfcs/SPEC-047-MIE.md` as the canonical enterprise standard",
        "Aetheris EKB, telemetry, execution, and planning artifacts under `.aetheris/`",
    ])))

    return intro + "\n" + "\n".join(sections) + "\n"


def generate() -> dict[str, Any]:
    RFC_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    created = []
    updated = []
    for spec in spec_records():
        metadata = collect_metadata(spec)
        target = existing_or_new_path(spec)
        existed = target.exists()
        content = render_spec(spec, metadata)
        target.write_text(content, encoding="utf-8", newline="\n")
        written.append(str(target.relative_to(ROOT)))
        if existed:
            updated.append(str(target.relative_to(ROOT)))
        else:
            created.append(str(target.relative_to(ROOT)))
    return {"written": written, "created": created, "updated": updated}


def validate() -> dict[str, Any]:
    failures = []
    specs = sorted(RFC_DIR.glob("SPEC-*.md"))
    seen_numbers = set()
    for path in specs:
        match = re.match(r"SPEC-(\d{3})-", path.name)
        if not match:
            continue
        seen_numbers.add(int(match.group(1)))
        text = path.read_text(encoding="utf-8", errors="ignore")
        for heading in REQUIRED_HEADINGS:
            if heading.upper() not in text:
                failures.append(f"{path.name}: missing heading {heading}")
        if "```mermaid" not in text:
            failures.append(f"{path.name}: missing Mermaid diagram")
        if "```plantuml" not in text:
            failures.append(f"{path.name}: missing PlantUML diagram")
        if "PLACEHOLDER" in text.upper() or "TODO" in text.upper():
            failures.append(f"{path.name}: contains placeholder language")

    expected = {spec.number for spec in spec_records()}
    missing = sorted(expected - seen_numbers)
    extra = sorted(seen_numbers - expected)
    if missing:
        failures.append(f"missing SPEC numbers: {missing}")
    if extra:
        failures.append(f"unexpected SPEC numbers: {extra}")
    return {
        "spec_count": len([n for n in seen_numbers if 1 <= n <= 65]),
        "missing": missing,
        "extra": extra,
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate the generated SPEC corpus instead of writing files.")
    args = parser.parse_args()

    if args.check:
        result = validate()
        print(json.dumps(result, indent=2))
        if result["failures"]:
            raise SystemExit(1)
        return

    result = generate()
    validation = validate()
    print(json.dumps({"generation": result, "validation": validation}, indent=2))
    if validation["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
