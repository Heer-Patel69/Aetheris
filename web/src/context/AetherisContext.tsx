import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import type { RuntimeState, BrainState, MissionState, ProjectHealth, SkillEntry, ModelUsage, ReplayStep, RfcSpecCoverage, IntegrationCard, MemoryLog } from '../types'

interface AetherisState {
  runtime: RuntimeState | null;
  brain: BrainState | null;
  mission: MissionState | null;
  health: ProjectHealth | null;
  skills: SkillEntry[];
  models: ModelUsage[];
  replay: ReplayStep[];
  rfcSpecs: RfcSpecCoverage[];
  integrations: IntegrationCard[];
  memoryLogs: MemoryLog[];
  loading: boolean;
}

const defaultState: AetherisState = {
  runtime: null,
  brain: null,
  mission: null,
  health: null,
  skills: [],
  models: [],
  replay: [],
  rfcSpecs: [],
  integrations: [],
  memoryLogs: [],
  loading: true,
};

const AetherisContext = createContext<AetherisState>(defaultState);

export function useAetheris() { return useContext(AetherisContext); }

export function AetherisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AetherisState>(defaultState);

  useEffect(() => {
    function generateLiveMockData() {
      const mockRuntime: RuntimeState = {
        brain_state: "IDLE",
        workflow_phase: "PLANNING_PHASE",
        active_goal: "Migrate Aetheris Workspace to .aetheris Directory",
        current_branch: "main",
        uptime_seconds: 12450 + Math.floor(Math.random() * 60),
        engines_online: 18,
        total_engines: 18,
        cpu_usage: 12 + Math.floor(Math.random() * 25),
        ram_usage: 45 + Math.floor(Math.random() * 5),
        gpu_usage: 0,
        events_per_second: Math.floor(Math.random() * 15)
      };

      const mockBrain: BrainState = {
        edo_state: "EXECUTION_PHASE",
        workflow_phase: "PLANNING_PHASE",
        decisions_made: 42,
        reasoning_latency_ms: 124,
        capabilities_resolved: 189,
        context_compression_ratio: 0.82,
        memory_retrievals: 73,
        execution_success_rate: 0.94
      };

      const mockMission: MissionState = {
        project_name: "Aetheris Core",
        current_goal: "Scaffold Mission Control Dashboard",
        milestone: "v1.0.0-Beta",
        sprint: "Sprint 4",
        health_score: 91,
        blockers: [],
        estimated_completion: "2026-07-10",
        active_roles: ["Architect", "Backend Engineer", "QA Auditor", "Product Manager"],
        tasks_completed: 18,
        tasks_total: 24
      };

      const mockHealth: ProjectHealth = {
        documentation: 85,
        architecture: 92,
        security: 80,
        testing: 74,
        performance: 88,
        maintainability: 90,
        technical_debt: 12,
        risk_index: 8
      };

      const mockModels: ModelUsage[] = [
        { model_name: "Claude 3.5 Sonnet", provider: "Anthropic", tokens_input: 450122, tokens_output: 120890, total_cost_usd: 6.84, latency_ms: 2200, success_rate: 98 },
        { model_name: "Gemini 1.5 Pro", provider: "Google", tokens_input: 890122, tokens_output: 220110, total_cost_usd: 3.12, latency_ms: 1800, success_rate: 95 },
        { model_name: "GPT-4o", provider: "OpenAI", tokens_input: 120400, tokens_output: 45900, total_cost_usd: 2.18, latency_ms: 2000, success_rate: 96 }
      ];

      const mockReplay: ReplayStep[] = [
        {
          step_number: 1,
          timestamp: "11:34:02",
          stage: "Intent",
          description: "Received user prompt to initialize dashboard and configure workspace manager",
          input_prompt: "now build phase 2",
          selected_capabilities: ["WorkspaceScaffolding", "UIGeneration"],
          loaded_skills: ["agency-ui-designer", "agency-rapid-prototyper"],
          models_used: ["Claude 3.5 Sonnet"],
          status: "success",
          files_modified: [],
          tokens_consumed: 2500,
          retries: 0
        },
        {
          step_number: 2,
          timestamp: "11:34:10",
          stage: "Capability Resolution",
          description: "CRE mapped prompt intent to structural UI directories and React component templates",
          input_prompt: "now build phase 2",
          selected_capabilities: ["WorkspaceMigration", "TypeScriptTypeValidation"],
          loaded_skills: ["agency-senior-developer"],
          models_used: ["Claude 3.5 Sonnet", "Gemini 1.5 Pro"],
          status: "success",
          files_modified: [],
          tokens_consumed: 4200,
          retries: 0
        }
      ];

      const mockRfcSpecs: RfcSpecCoverage[] = [
        { id: "RFC-001", title: "Project Workspace Specification", type: "RFC", coverage_percentage: 100, referenced_skills: ["agency-senior-developer"], missing_implementations: [], verification_status: "passed" },
        { id: "RFC-002", title: "3-Level Indexing Core Pattern", type: "RFC", coverage_percentage: 85, referenced_skills: ["agency-solidity-smart-contract-engineer"], missing_implementations: ["Warm Cache Sync"], verification_status: "warning" },
        { id: "SPEC-010", title: "Security Threat Containment", type: "SPEC", coverage_percentage: 90, referenced_skills: ["agency-penetration-tester"], missing_implementations: ["Docker Outbound Restrictions"], verification_status: "passed" }
      ];

      const mockIntegrations: IntegrationCard[] = [
        { name: "Headroom Adapter", adapter_health: "healthy", latency_ms: 124, version: "v1.2.0", capabilities_mapped: 12, compatibility_score: 95 },
        { name: "Everything Claude Code (ECC)", adapter_health: "healthy", latency_ms: 220, version: "v2.1.0", capabilities_mapped: 8, compatibility_score: 92 },
        { name: "Claude Templates", adapter_health: "warning", latency_ms: 380, version: "v0.9.1", capabilities_mapped: 4, compatibility_score: 85 }
      ];

      const mockMemoryLogs: MemoryLog[] = [
        { id: "MEM-4910", timestamp: "11:15:30", category: "decision", title: "Hidden Workspace Directory Structure", description: "Consolidated all local project engineering documentation, memory layers, and assets inside a hidden project root directory .aetheris/." },
        { id: "MEM-4911", timestamp: "11:16:10", category: "rejected_idea", title: "Global SQLite Database Storage", description: "Rejected the proposal to host the 3-level index globally in a shared SQLite DB. Decided to provision dedicated local vector DB endpoints." },
        { id: "MEM-4912", timestamp: "11:17:45", category: "lesson_learned", title: "Async event execution limits", description: "Encountered thread deadlock during parallel RSE execution. Set explicit asyncio task group limits to prevent thread starvation." }
      ];

      setState({
        runtime: mockRuntime,
        brain: mockBrain,
        mission: mockMission,
        health: mockHealth,
        skills: [],
        models: mockModels,
        replay: mockReplay,
        rfcSpecs: mockRfcSpecs,
        integrations: mockIntegrations,
        memoryLogs: mockMemoryLogs,
        loading: false
      });
    }

    generateLiveMockData();
    const interval = setInterval(generateLiveMockData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <AetherisContext.Provider value={state}>
      {children}
    </AetherisContext.Provider>
  );
}
