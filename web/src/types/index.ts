export interface RuntimeState {
  brain_state: string;
  workflow_phase: string;
  active_goal: string;
  current_branch: string;
  uptime_seconds: number;
  engines_online: number;
  total_engines: number;
  cpu_usage: number;
  ram_usage: number;
  gpu_usage: number;
  events_per_second: number;
}

export interface ExecutionState {
  current_task: string;
  queue_depth: number;
  workers_active: number;
  workers_total: number;
  scheduler_state: string;
}

export interface SkillEntry {
  id: string;
  name: string;
  category: string;
  cache_tier: 'hot' | 'warm' | 'cold';
  success_rate: number;
  execution_time_ms: number;
  quality_score: number;
  last_used: string;
}

export interface ProjectHealth {
  documentation: number;
  architecture: number;
  security: number;
  testing: number;
  performance: number;
  maintainability: number;
  technical_debt: number;
  risk_index: number;
}

export interface BrainState {
  edo_state: string;
  workflow_phase: string;
  decisions_made: number;
  reasoning_latency_ms: number;
  capabilities_resolved: number;
  context_compression_ratio: number;
  memory_retrievals: number;
  execution_success_rate: number;
}

export interface MissionState {
  project_name: string;
  current_goal: string;
  milestone: string;
  sprint: string;
  health_score: number;
  blockers: string[];
  estimated_completion: string;
  active_roles: string[];
  tasks_completed: number;
  tasks_total: number;
}

export interface ModelUsage {
  model_name: string;
  provider: string;
  tokens_input: number;
  tokens_output: number;
  total_cost_usd: number;
  latency_ms: number;
  success_rate: number;
}

export interface ReplayStep {
  step_number: number;
  timestamp: string;
  stage: string;
  description: string;
  input_prompt: string;
  selected_capabilities: string[];
  loaded_skills: string[];
  models_used: string[];
  status: 'success' | 'warning' | 'error';
  files_modified: string[];
  tokens_consumed: number;
  retries: number;
}

export interface RfcSpecCoverage {
  id: string;
  title: string;
  type: 'RFC' | 'SPEC';
  coverage_percentage: number;
  referenced_skills: string[];
  missing_implementations: string[];
  verification_status: 'passed' | 'warning' | 'failed';
}

export interface IntegrationCard {
  name: string;
  adapter_health: 'healthy' | 'warning' | 'unhealthy';
  latency_ms: number;
  version: string;
  capabilities_mapped: number;
  compatibility_score: number;
}

export interface MemoryLog {
  id: string;
  timestamp: string;
  category: 'decision' | 'rejected_idea' | 'lesson_learned' | 'coding_standard';
  title: string;
  description: string;
}

export type NavScreen =
  | 'overview'
  | 'mission'
  | 'brain'
  | 'runtime'
  | 'engineering'
  | 'skills'
  | 'rfc'
  | 'spec'
  | 'integrations'
  | 'knowledge-graph'
  | 'replay'
  | 'analytics'
  | 'memory'
  | 'settings';
