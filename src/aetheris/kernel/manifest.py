import yaml
from pathlib import Path

DEFAULT_MANIFEST_YAML = """# Aetheris Engineering Operating System Manifest
project:
  name: "Official Aetheris Website"
  goal: "Build a premium full-stack website demonstrating Aetheris capabilities, including Landing Page, interactive dashboard, docs, and search."
  version: "1.0.0"

engineering_laws:
  - "Aetheris is the Engineering Hypervisor. External systems never own the workflow."
  - "The Kernel always owns Planning, Lifecycle, State, Verification, Memory, Repository Intelligence, Skill Routing, and Benchmarking."
  - "Headroom, ECC, Claude Code templates, and LLMs are implementation providers only."

phase_order:
  - "Phase 1: Repository Discovery"
  - "Phase 2: Business Discovery"
  - "Phase 3: Product Discovery"
  - "Phase 4: Requirement Discovery"
  - "Phase 5: Capability Discovery"
  - "Phase 6: Department Discovery"
  - "Phase 7: Skill Discovery"
  - "Phase 8: RFC Resolution"
  - "Phase 9: SPEC Resolution"
  - "Phase 10: Architecture"
  - "Phase 11: Database"
  - "Phase 12: Backend"
  - "Phase 13: Frontend"
  - "Phase 14: Security"
  - "Phase 15: Testing"
  - "Phase 16: Documentation"
  - "Phase 17: Deployment"
  - "Phase 18: Verification"
  - "Phase 19: Benchmark"
  - "Phase 20: Update .aetheris"

required_artifacts:
  - "BRD"
  - "PRD"
  - "SRS"
  - "TRD"
  - "Architecture"
  - "ER Diagram"
  - "Sequence Diagram"
  - "Component Diagram"
  - "Deployment Diagram"
  - "OpenAPI"
  - "Database Schema"
  - "Security Review"
  - "Threat Model"
  - "Design System"
  - "UI Guidelines"
  - "Engineering Plan"
  - "Implementation Plan"
  - "Risk Analysis"
  - "Testing Plan"
  - "Deployment Guide"
  - "Rollback Guide"
  - "Operations Manual"
  - "Benchmark Report"
  - "Final Audit"

quality_gates:
  architecture_review:
    enabled: true
    standards: ["SOLID", "Clean Architecture", "Topological Imports"]
  security_review:
    enabled: true
    standards: ["OWASP Top 10", "No Hardcoded Secrets", "Sanitized Inputs"]
  performance_review:
    enabled: true
    standards: ["No Nested Loops > O(N^2)", "Framer Motion Optimal Performance"]
  accessibility_review:
    enabled: true
    standards: ["WCAG 2.1 AA", "Aria Attributes", "Keyboard Navigation"]
  testing_review:
    enabled: true
    standards: ["Coverage >= 90%", "End-to-End Success"]
  documentation_review:
    enabled: true
    standards: ["OpenAPI Compliance", "Updated Readme", "Inline Docstrings"]
  benchmark_review:
    enabled: true
    standards: ["Lighthouse >= 95", "Execution Overhead Control"]

provider_configuration:
  llm_model: "Gemini 3.5 Flash (High)"
  router:
    fallback: "claude-3-5-sonnet"
    routing_logic: "cost-and-latency-optimized"
  headroom:
    compression_enabled: true
    target_ratio: 0.45
  ecc:
    enabled: true
    hooks: ["pre-commit", "post-build", "auto-recovery"]

benchmark_thresholds:
  repository_coverage_percentage: 95.0
  lighthouse_score: 95.0
  min_test_coverage: 90.0
  max_execution_time_seconds: 600
  token_savings_percentage: 45.0
  cost_savings_percentage: 50.0

ui_standards:
  aesthetics: ["Apple", "Stripe", "Linear", "Vercel", "Raycast"]
  theme: "Sleek Dark Mode"
  libraries:
    - "Three.js"
    - "Framer Motion"
    - "TailwindCSS"
    - "Lenis"
  features:
    - "Glassmorphism"
    - "Mouse Interaction"
    - "Parallax Scroll"
    - "Micro-animations"

security_policies:
  auth_type: "JWT + RBAC"
  rate_limiting:
    enabled: true
    max_requests_per_minute: 100
  encryption:
    algorithm: "AES-256-GCM"
    keys: "environment-bound"

deployment_targets:
  platform: "Netlify"
  database: "PostgreSQL"
  cache: "Redis"
  containerization: "Docker"
  ci_cd: "GitHub Actions"
"""

def create_default_manifest(target_path: Path):
    """Creates a default manifest.yaml file at the specified path."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(DEFAULT_MANIFEST_YAML, encoding="utf-8")
