export interface RFC {
  id: string;
  title: string;
  status: "RATIFIED" | "DRAFT" | "PROPOSED";
  purpose: string;
  modules: string[];
  dependencies: string[];
  architecture: string;
  bestPractices: string[];
  antiPatterns: string[];
  mermaidDiagram: string;
}

export const rfcs: RFC[] = [
  {
    id: "RFC-000",
    title: "Kernel Architecture & Scheduling",
    status: "RATIFIED",
    purpose: "Establishes the core modular layer division, event bus protocol, and dynamic scheduling constitution.",
    modules: ["Core Kernel Orchestrator", "Unified Event Bus", "Sandbox Security Manager"],
    dependencies: [],
    architecture: "Defines the core bootstrap lifecycle, process sandbox boundaries, and event propagation layers.",
    bestPractices: ["Always enforce sandbox path checks", "Decouple state changes from visual outputs"],
    antiPatterns: ["Executing raw commands outside the sandbox", "Direct file edits bypassing the Event Bus"],
    mermaidDiagram: `graph TD;
      A[Kernel Orchestrator] --> B[Event Bus];
      B --> C[Sandbox Security];
      C --> D[Target Workspace];`
  },
  {
    id: "RFC-001",
    title: "Engineering Knowledge System (EKS)",
    status: "RATIFIED",
    purpose: "Governs workspace analysis, file indexing, and knowledge compilation.",
    modules: ["Workspace Directory Scanner", "Engineering Graph Engine", "Fact Verification Engine"],
    dependencies: ["RFC-000"],
    architecture: "Leverages topological code graphs to maintain a version-controlled index of all files, dependencies, and exports.",
    bestPractices: ["Cache fingerprints to reduce scan times", "Use topological sort for dependecy resolution"],
    antiPatterns: ["Scanning node_modules or standard ignore directories", "Caching outdated compilation records"],
    mermaidDiagram: `graph TD;
      A[Directory Scanner] --> B[Fingerprint Cache];
      B --> C[Dependency Graph Builder];`
  },
  {
    id: "RFC-002",
    title: "Requirement Understanding System (RUS)",
    status: "RATIFIED",
    purpose: "Ingests user goals, analyzes project conventions, and maps objectives to system capabilities.",
    modules: ["Goal Manager", "Completeness Auditor", "Tech Decision Engine"],
    dependencies: ["RFC-001"],
    architecture: "Translates high-level specifications into normalized technical objectives.",
    bestPractices: ["Define clear boundaries for user intent", "Verify technical feasibility before plan compilation"],
    antiPatterns: ["Accepting vague prompt inputs without audit logs", "Bypassing tech decision evaluations"],
    mermaidDiagram: `graph TD;
      A[Raw Intent] --> B[Goal Manager];
      B --> C[Completeness Auditor];
      C --> D[Tech Decision Engine];`
  },
  {
    id: "RFC-003",
    title: "Product Planning System (PPS)",
    status: "RATIFIED",
    purpose: "Decomposes goals into sequential feature maps and dependency trees.",
    modules: ["Feature Matrix Engine", "Timeline Scheduler", "Risk Profiler"],
    dependencies: ["RFC-002"],
    architecture: "Generates high-fidelity product requirements documents (PRDs) and business requirements documents (BRDs).",
    bestPractices: ["Compile incremental features", "Define clear user personas and objectives"],
    antiPatterns: ["Planning features with circular dependencies", "Underestimating task complexity profiles"],
    mermaidDiagram: `graph TD;
      A[Requirements] --> B[Feature Matrix];
      B --> C[Timeline Scheduler];
      C --> D[PRD Output];`
  },
  {
    id: "RFC-004",
    title: "Architecture Planning System (APS)",
    status: "RATIFIED",
    purpose: "Designs system models, database tables, and import structures.",
    modules: ["Domain Architecture Builder", "Database Schema Generator", "Integrity Validator"],
    dependencies: ["RFC-003"],
    architecture: "Enforces strict structural boundaries, preventing cyclic dependency loops.",
    bestPractices: ["Validate import directions", "Maintain clear schema separation maps"],
    antiPatterns: ["Hardcoding database keys without validation", "Bypassing integrity checks on entity updates"],
    mermaidDiagram: `graph TD;
      A[Feature Map] --> B[Domain Builder];
      B --> C[Schema Generator];
      C --> D[Architecture Plan];`
  },
  {
    id: "RFC-005",
    title: "Engineering Asset System (EAS)",
    status: "DRAFT",
    purpose: "Manages asset reuse (templates, modules, styling tokens) to prevent duplicate efforts.",
    modules: ["Asset Registry", "Component Compiler", "Design System Adaptor"],
    dependencies: ["RFC-004"],
    architecture: "Indexes existing UI libraries and backend utilities to guide the developer agent.",
    bestPractices: ["Prioritize component reuse", "Strictly align layout templates with the design system"],
    antiPatterns: ["Generating inline styles instead of CSS classes", "Generating redundant CRUD utility scripts"],
    mermaidDiagram: `graph TD;
      A[Asset Registry] --> B[Component Selector];
      B --> C[Design System Validator];`
  },
  {
    id: "RFC-006",
    title: "Skill Intelligence System (SIS)",
    status: "RATIFIED",
    purpose: "Dispatches and ranks agentic capabilities based on performance benchmarks.",
    modules: ["Skill Matcher", "Benchmark Runner", "Specialist Router"],
    dependencies: ["RFC-003"],
    architecture: "Routes specific implementation tasks to verified execution specialists.",
    bestPractices: ["Score skills dynamically", "Validate dependencies between skills before scheduling"],
    antiPatterns: ["Dispatching non-expert skills for database migrations", "Bypassing skill benchmark evaluations"],
    mermaidDiagram: `graph TD;
      A[Task Item] --> B[Skill Matcher];
      B --> C[Specialist Router];`
  },
  {
    id: "RFC-007",
    title: "Model Intelligence System (MIS)",
    status: "RATIFIED",
    purpose: "Tracks cost and latency limits to route execution steps to optimized model nodes.",
    modules: ["Token Budget Controller", "Cost Estimator", "Provider Router"],
    dependencies: ["RFC-006"],
    architecture: "Optimizes latency-critical vs reasoning-heavy model dispatch targets.",
    bestPractices: ["Enforce context size limits", "Select cheaper model endpoints for routine formatting"],
    antiPatterns: ["Using maximum parameter models for regex replacement", "Exceeding token budgets without checkpoints"],
    mermaidDiagram: `graph TD;
      A[Specialist Query] --> B[Token Controller];
      B --> C[Optimal Model Route];`
  },
  {
    id: "RFC-008",
    title: "Autonomous Execution System (AES)",
    status: "RATIFIED",
    purpose: "Executes parallel code generation, testing, and continuous deployment tasks.",
    modules: ["Code Editor Engine", "Test Executor", "Release Orchestrator"],
    dependencies: ["RFC-004", "RFC-007"],
    architecture: "Orchestrates sandbox execution schedules with Git version control.",
    bestPractices: ["Always build changes before committing", "Run tests inside isolated environments"],
    antiPatterns: ["Direct execution without a preview check", "Deploying changes that fail compilation"],
    mermaidDiagram: `graph TD;
      A[Code Generation] --> B[Isolated Builder];
      B --> C[Test Suite];
      C --> D[Git Commit];`
  },
  {
    id: "RFC-009",
    title: "Verification & Quality System (VQS)",
    status: "RATIFIED",
    purpose: "Enforces strict compliance audits including clean code standards, security scans, and WCAG rules.",
    modules: ["DoD Auditor", "Security Scanner", "Accessibility Validator"],
    dependencies: ["RFC-008"],
    architecture: "Enforces Definition of Done verification loops before final checkins.",
    bestPractices: ["Scan for secret leakage on commit", "Verify accessibility rules at build time"],
    antiPatterns: ["Bypassing DoD checks to speed up releases", "Skipping security audits during hotfixes"],
    mermaidDiagram: `graph TD;
      A[Build Output] --> B[DoD Auditor];
      B --> C[Security Scan];
      C --> D[Release Approval];`
  }
];
