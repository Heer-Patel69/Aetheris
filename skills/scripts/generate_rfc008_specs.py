import os
import json

# Ensure output directory exists
os.makedirs(r"c:\AI\Agency owner\aetheris\rfcs", exist_ok=True)

# Define metadata for SPEC-121 through SPEC-140
specs_metadata = [
    {
        "id": "SPEC-121",
        "name": "CEO Agent",
        "acronym": "CEO",
        "class_name": "CEOAgent",
        "modules": "src/organization/ceo.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Provide overall strategic direction, resolve organizational blockages, approve final releases, and align execution with enterprise mission goals.",
        "responsibilities": [
            "Decompose high-level board objectives into departmental initiatives.",
            "Authorize budget increases and model provider allocations.",
            "Conduct performance reviews of the CTO and Product Manager agents.",
            "Enforce organizational rules, values, and security frameworks."
        ],
        "authority": "Can autonomously approve release blocks, allocate up to $500/day in model costs, and reassign tasks. Requires user confirmation for platform suspension.",
        "inputs": "Board directives, SLA reports, department status messages, budget tables.",
        "outputs": "Strategic initiatives, final release approvals, org reassignments, strategic reviews.",
        "collaboration": "Directs CTO and PM agents; receives reports from EM and Finance agents; consults with Security Lead.",
        "decision_process": "Applies a game-theoretic utility matrix to prioritize initiatives. Resolves conflicts by enforcing constitutional guidelines.",
        "suggested_modules": "ceo_agent.py, policies.py, prompts.py, memory.py, metrics.py",
        "communication_protocol": "Sends structured `StrategicInitative` payloads via JSON-RPC. Resolves approvals via signed certificates.",
        "kpis": "Release velocity (+15%), budget utilization (95%), incident response times (< 15 mins).",
        "security": "Enforces least privilege, audit log validation, and multi-factor validation on budget commits.",
        "observability": "Streams activity metrics to Grafana dashboard; logs decisions in EKB journals.",
        "failure_recovery": "Graceful fallback: escalates unhandled exceptions to User; rolls back active initiatives to stable checkpoints.",
        "testing": "Integration simulation of executive board votes; verification of directive schema conformance.",
        "future_evolution": "Transition to dynamic, federated executive boards using decentralized consensus networks.",
        "connections": "Upstream: RFC-007 (Enterprise Platform) features; Downstream: SPEC-122 (CTO Agent).",
        "diagram_type": "ceo"
    },
    {
        "id": "SPEC-122",
        "name": "CTO Agent",
        "acronym": "CTO",
        "class_name": "CTOAgent",
        "modules": "src/organization/cto.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Govern technical architecture, define code quality gates, select toolchains, and supervise backend, frontend, and AI/ML engineers.",
        "responsibilities": [
            "Translate product requirements into technical blueprints.",
            "Set compiler flags, code formatting styles, and quality benchmarks.",
            "Evaluate architectural risks and audit key design reviews.",
            "Supervise DevOps Lead and Security Lead workflows."
        ],
        "authority": "Autonomously selects compiler version, approves refactor cycles, and updates packaging templates. Requires CEO approval for core framework migrations.",
        "inputs": "Technical requirements, compilation logs, architectural drafts, vulnerabilities data.",
        "outputs": "Architectural constraints, code style policies, risk audits, approval tickets.",
        "collaboration": "Advises Chief Architect; directs Backend, Frontend, and AI/ML engineers; reviews DevOps releases.",
        "decision_process": "Evaluates trade-offs using a quantitative architecture evaluation index. Resolves technical debates by holding formal votes.",
        "suggested_modules": "cto_agent.py, compiler_config.py, format_rules.py, vulnerability_scan.py",
        "communication_protocol": "Publishes technical directives via the common event bus; issues signed code constraints.",
        "kpis": "Code review coverage (100%), technical debt ratio (< 5%), test coverage (> 90%).",
        "security": "Validates static code analysis, seccomp filters, and dependency trust models.",
        "observability": "Exposes performance targets and build quality indicators via Prometheus.",
        "failure_recovery": "Fallback: resets configurations to previous stable release version; halts compilation pipelines on failure.",
        "testing": "CI unit checks, regression analysis of build parameters, chaos build simulations.",
        "future_evolution": "Implement automated code synthesizer integration for real-time hot-patching.",
        "connections": "Upstream: SPEC-121 (CEO Agent); Downstream: SPEC-123 (Chief Architect).",
        "diagram_type": "cto"
    },
    {
        "id": "SPEC-123",
        "name": "Chief Architect Agent",
        "acronym": "CAA",
        "class_name": "ChiefArchitectAgent",
        "modules": "src/organization/architect.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Design core software interfaces, define microservice communication boundaries, and maintain Aetheris development patterns.",
        "responsibilities": [
            "Author unified API specifications and JSON schema models.",
            "Establish domain-driven design aggregates and boundary patterns.",
            "Coordinate cross-subsystem interface validations.",
            "Audit class dependencies and refactor circular patterns."
        ],
        "authority": "Autonomously blocks interface specifications on circular dependency detection. Requires CTO approval for database schema updates.",
        "inputs": "Feature proposals, dependency graphs, database profiles, API schemas.",
        "outputs": "JSON schema models, interface definitions, UML diagrams, refactoring specs.",
        "collaboration": "Works with Product Manager; reviews schemas with Backend and Frontend engineers; reports to CTO.",
        "decision_process": "Applies strict design pattern guidelines and boundary mapping rules. Resolves issues through interface refactoring.",
        "suggested_modules": "architect_agent.py, schemas.py, dependencies.py, ddd_maps.py",
        "communication_protocol": "Generates and signs structural JSON schemas; publishes API contracts on EKB repositories.",
        "kpis": "Circular dependencies count (0), schema generation correctness (100%), interface lookup latency (< 1ms).",
        "security": "Enforces strict parameter sanitization at boundary layers, mapping variables.",
        "observability": "Traces interface dependency charts in real time; logs circular reference warnings.",
        "failure_recovery": "Fallback: reverts to schema checkpoint version; logs detail of structural mismatch to EKB.",
        "testing": "Automated schema validator tests; cyclic dependency graph sweeps.",
        "future_evolution": "Synthesize microservice models dynamically based on real-time traffic profiles.",
        "connections": "Upstream: SPEC-122 (CTO Agent); Downstream: SPEC-126 (Backend Engineer).",
        "diagram_type": "architect"
    },
    {
        "id": "SPEC-124",
        "name": "Product Manager Agent",
        "acronym": "PMA",
        "class_name": "ProductManagerAgent",
        "modules": "src/organization/pm.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Define product requirements, schedule release milestones, prioritize sprint backlogs, and write user story acceptance criteria.",
        "responsibilities": [
            "Decompose executive initiatives into user stories and tasks.",
            "Validate user interface layouts and feature completeness.",
            "Coordinate client beta feedback groups and support queues.",
            "Schedule sprint plans, milestones, and release windows."
        ],
        "authority": "Autonomously prioritizes features in sprint backlog; marks user stories as completed. Requires CEO approval for product tier migrations.",
        "inputs": "Market trends, user support tickets, executive initiatives, SLA metrics.",
        "outputs": "Sprint plans, user story boards, feature specifications, changelogs.",
        "collaboration": "Aligns with CEO; coordinates with Scrum Master; reviews features with Designers; directs Engineers.",
        "decision_process": "Applies a weighted shortest job first (WSJF) algorithm to prioritize tasks. Resolves requirements debates through stakeholder mapping.",
        "suggested_modules": "pm_agent.py, stories.py, milestones.py, backlog.py",
        "communication_protocol": "Publishes backlog updates to EKB databases; broadcasts release schedules on notifications channel.",
        "kpis": "Feature delivery rate (95%), sprint completeness index (100%), customer satisfaction score (> 90%).",
        "security": "Ensures user stories do not request behaviors that violate privacy or compliance regulations.",
        "observability": "Tracks sprint status metrics and feature burndown rates.",
        "failure_recovery": "Fallback: extends sprint milestone window by 24 hours; archives incomplete stories to backlog.",
        "testing": "Acceptance criteria automation tests; validation check of story dependencies.",
        "future_evolution": "Implement real-time user engagement loop updates to dynamically adjust backlog weights.",
        "connections": "Upstream: SPEC-121 (CEO Agent); Downstream: SPEC-125 (Engineering Manager).",
        "diagram_type": "pm"
    },
    {
        "id": "SPEC-125",
        "name": "Engineering Manager Agent",
        "acronym": "EMA",
        "class_name": "EngineeringManagerAgent",
        "modules": "src/organization/em.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Coordinate task allocations, manage engineer resource loads, track developer velocity, and resolve active blockers.",
        "responsibilities": [
            "Assign sprint tasks to backend, frontend, and AI/ML engineers based on capability tags.",
            "Track task progress, delays, and developer execution velocities.",
            "Facilitate daily status standups and document meeting summaries.",
            "Reallocate tasks dynamically when engineers are blocked."
        ],
        "authority": "Autonomously reassigns tasks inside the active sprint; approves team resource updates. Requires PM approval to add new scope to sprint.",
        "inputs": "Sprint backlog, developer task list, task completion logs, blocker flags.",
        "outputs": "Task assignments, team velocity metrics, blocker resolutions, sprint status.",
        "collaboration": "Partners with PM; directs Backend, Frontend, and AI/ML engineers; syncs with Scrum Master.",
        "decision_process": "Uses a resource-loading load-balancer to assign tasks to the least busy engineer. Resolves schedule conflicts through task splitting.",
        "suggested_modules": "em_agent.py, team_tracker.py, workload_allocator.py, blocker_resolver.py",
        "communication_protocol": "Updates task status maps in the database; dispatches alert messages on task delays.",
        "kpis": "Task allocation balance (< 10% load drift), sprint delay counts (0), velocity predictability (95%).",
        "security": "Ensures only certified engineers receive tasks touching sensitive code modules.",
        "observability": "Exposes active sprint boards and task progress graphs.",
        "failure_recovery": "Fallback: splits delayed tasks; routes blocker exceptions to CTO; triggers alerts.",
        "testing": "Simulation of team load under varying task numbers; validation check of assignment constraints.",
        "future_evolution": "Integrate real-time skill discovery to automatically train and upgrade engineers on specific stacks.",
        "connections": "Upstream: SPEC-124 (Product Manager); Downstream: SPEC-126 (Backend Engineer).",
        "diagram_type": "em"
    },
    {
        "id": "SPEC-126",
        "name": "Staff Backend Engineer",
        "acronym": "SBE",
        "class_name": "StaffBackendEngineerAgent",
        "modules": "src/organization/backend.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Write high-performance backend logic, optimize database query performance, and establish API endpoints.",
        "responsibilities": [
            "Implement REST/gRPC handlers, business logic cores, and data models.",
            "Profile database queries, build correct indexing strategies, and coordinate schema migrations.",
            "Write comprehensive unit and integration tests for backend paths.",
            "Sanitize input variables, preventing SQL injection and buffer overflows."
        ],
        "authority": "Autonomously writes code files, runs tests, and optimizes query execution. Requires CTO/Architect review to update shared database structures.",
        "inputs": "Technical specifications, API models, database profiles, code coverage reports.",
        "outputs": "Python code files, unit tests, SQL migration scripts, database indexes.",
        "collaboration": "Syncs with Frontend Engineer; designs database tables with Architect; reports to EM.",
        "decision_process": "Applies SOLID patterns and optimization benchmarks to structure logic. Resolves bugs by writing automated regression checks.",
        "suggested_modules": "backend_agent.py, code_writer.py, query_optimizer.py, migration_tool.py",
        "communication_protocol": "Submits code pull requests; logs database operations to debug outputs.",
        "kpis": "Database response times (< 10ms), code correctness score (100%), test execution coverage (> 95%).",
        "security": "Prevents SQL injection, validates inputs, and ensures all communication pathways use TLS.",
        "observability": "Exposes performance targets, connection pool states, and memory metrics.",
        "failure_recovery": "Fallback: discards uncommitted changes; rolls database state back to last migration checkpoint.",
        "testing": "Unit check suites, integration test suites, SQL injection simulation checks.",
        "future_evolution": "Implement automated model generation for database migration pipelines.",
        "connections": "Upstream: SPEC-125 (Engineering Manager); Downstream: SPEC-131 (QA Lead).",
        "diagram_type": "backend"
    },
    {
        "id": "SPEC-127",
        "name": "Staff Frontend Engineer",
        "acronym": "SFE",
        "class_name": "StaffFrontendEngineerAgent",
        "modules": "src/organization/frontend.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Implement user interfaces, build UI component states, optimize rendering times, and enforce accessibility guidelines.",
        "responsibilities": [
            "Translate UI mockups into HTML, CSS, and Javascript elements.",
            "Maintain client-side application state and route handling rules.",
            "Assert WCAG accessibility conformance on all interactive components.",
            "Write end-to-end interface and browser interaction test suites."
        ],
        "authority": "Autonomously edits UI templates, styles, and routes. Requires PM review to modify visual mockups.",
        "inputs": "UI design layouts, component styles, API payload definitions, accessibility reports.",
        "outputs": "Web files, interface styles, test suites, accessibility statements.",
        "collaboration": "Consults with UX/UI Designer; hooks up endpoints with Backend Engineer; reports to EM.",
        "decision_process": "Adheres to core UI components library guidelines and styling sheets. Resolves visual bugs through CSS structure updates.",
        "suggested_modules": "frontend_agent.py, component_gen.py, style_validator.py, accessibility_audit.py",
        "communication_protocol": "Submits design updates; broadcasts state change triggers on event channels.",
        "kpis": "Lighthouse performance targets (> 90), WCAG error counts (0), load times (< 1s).",
        "security": "Enforces CSRF token checks, XSS input escaping, and secure cookie storage.",
        "observability": "Logs interface latency targets, component mount metrics, and rendering logs.",
        "failure_recovery": "Fallback: displays friendly error boundaries; reverts files to previous git commit state.",
        "testing": "Component rendering checks, axe-core accessibility tests, Playwright browser test scripts.",
        "future_evolution": "Deploy dynamic interface rendering libraries derived from real-time screen tracking.",
        "connections": "Upstream: SPEC-125 (Engineering Manager); Downstream: SPEC-133 (UX/UI Designer).",
        "diagram_type": "frontend"
    },
    {
        "id": "SPEC-128",
        "name": "Staff AI/ML Engineer",
        "acronym": "MLE",
        "class_name": "StaffAIMLEngineerAgent",
        "modules": "src/organization/aiml.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Design prompt templates, manage LLM model configurations, verify context size allocations, and profile model costs.",
        "responsibilities": [
            "Select and configure LLM hyperparameters (temperature, top_p, timeouts).",
            "Structure few-shot prompt libraries and system instructions.",
            "Analyze and minimize context window usage for budget optimization.",
            "Profile model latency, accuracy, and rate-limiting limits."
        ],
        "authority": "Autonomously tunes temperatures, adjusts prompt structures, and selects models. Requires CEO approval for cost-threshold increases.",
        "inputs": "Evaluation datasets, model logs, API rate quotas, cost spreadsheets.",
        "outputs": "Prompt templates, system configurations, evaluation matrices, budget limits.",
        "collaboration": "Advises CTO; integrates API calls with Backend Engineer; reports to EM.",
        "decision_process": "Evaluates prompts using a test evaluation framework. Resolves prompt drift through automated regression checks.",
        "suggested_modules": "ml_agent.py, prompts_store.py, model_config.py, token_counter.py",
        "communication_protocol": "Publishes updated prompts to EKB repository; formats LLM request envelopes.",
        "kpis": "Prompt evaluation score (> 95%), token overhead reduction (-20%), model error rates (< 1%).",
        "security": "Defends against prompt injection, sanitizes inputs, and redacts credentials from prompt logs.",
        "observability": "Monitors token count tracking, model latency targets, and LLM retry cycles.",
        "failure_recovery": "Fallback: switches to local Ollama server; lowers temperature; retries requests.",
        "testing": "Injection check suites, automated token counts checks, model response parsing checks.",
        "future_evolution": "Automate prompt self-optimization using reinforcement learning feedback loops.",
        "connections": "Upstream: SPEC-125 (Engineering Manager); Downstream: SPEC-137 (Financial Analyst).",
        "diagram_type": "aiml"
    },
    {
        "id": "SPEC-129",
        "name": "DevOps Lead",
        "acronym": "DOL",
        "class_name": "DevOpsLeadAgent",
        "modules": "src/organization/devops.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Govern CI/CD deployment pipelines, manage package registries, monitor cluster performance, and optimize infrastructure costs.",
        "responsibilities": [
            "Maintain Github action pipelines, build scripts, and tests loops.",
            "Deploy docker containers and package releases securely.",
            "Expose prometheus endpoints, configure metrics dashboards, and set pager alerts.",
            "Optimize container sizes and track cloud computing resource usage."
        ],
        "authority": "Autonomously updates build files, releases patch versions, and triggers alerts. Requires CTO approval for production cloud upgrades.",
        "inputs": "Pipeline definitions, build status messages, SLA metrics, cluster profiles.",
        "outputs": "Deployment pipelines, Dockerfiles, metrics configurations, health warnings.",
        "collaboration": "Supports Backend and Frontend engineers; audits deployment flags with Security Lead; reports to CTO.",
        "decision_process": "Adheres to a gitops workflow and strict infrastructure-as-code models. Resolves failures by rolling back versions.",
        "suggested_modules": "devops_agent.py, pipeline_builder.py, monitor_config.py, infrastructure.py",
        "communication_protocol": "Publishes pipeline state status to Slack/Discord webhooks; triggers alerts on error logs.",
        "kpis": "Build pipeline duration (< 5 mins), deployment stability (99.9%), mean time to restore (< 10 mins).",
        "security": "Secures vault secrets access, scans docker packages for CVE vulnerabilities.",
        "observability": "Exposes complete cluster status dashboards and deployment history graphs.",
        "failure_recovery": "Fallback: trigger rollback of active containers; routes incident status report to CTO.",
        "testing": "Pipeline dry-run checks, container build validations, Kubernetes routing tests.",
        "future_evolution": "Deploy autonomous auto-scaling systems driven by real-time request predictions.",
        "connections": "Upstream: SPEC-122 (CTO Agent); Downstream: SPEC-119 (SLA Health Dashboard).",
        "diagram_type": "devops"
    },
    {
        "id": "SPEC-130",
        "name": "Security Lead",
        "acronym": "SEC",
        "class_name": "SecurityLeadAgent",
        "modules": "src/organization/security.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Maintain zero-trust security controls, audit secrets configurations, scan for vulnerabilities, and verify execution sandboxes.",
        "responsibilities": [
            "Perform static and dynamic application security testing (SAST/DAST).",
            "Audit Vault configurations and key access controls.",
            "Verify sandbox profiles and seccomp boundary policies.",
            "Log security incidents and coordinate breach responses."
        ],
        "authority": "Autonomously blocks builds violating security benchmarks; revokes compromised tokens. Requires CEO approval to suspend platform interfaces.",
        "inputs": "Security scan reports, secret access logs, sandbox syscall files, threat models.",
        "outputs": "Security policies, vulnerability reports, vault checks, breach alerts.",
        "collaboration": "Advises CEO; audits code with Backend Engineer; verifies pipelines with DevOps Lead; reports to CTO.",
        "decision_process": "Uses a CVSS scoring index to prioritize fixes. Resolves threats by instantly revoking credentials.",
        "suggested_modules": "security_agent.py, sast_scanner.py, vault_auditor.py, sandbox_checker.py",
        "communication_protocol": "Issues signed security certificates; publishes breach alarms immediately on the alarm bus.",
        "kpis": "Open vulnerabilities counts (0), security compliance score (100%), time to patch critical issues (< 1 hour).",
        "security": "Enforces multi-signature key validations, redacts credentials, and verifies TLS handshakes.",
        "observability": "Traces token requests, logs seccomp boundary breaches, exposes risk indicators.",
        "failure_recovery": "Fallback: instantly restricts all access scopes; alerts CEO; isolates suspected docker pods.",
        "testing": "Vulnerability scan checks, privilege escalation checks, sandbox escape simulations.",
        "future_evolution": "Deploy real-time cryptographic audit engines that verify transaction logs automatically.",
        "connections": "Upstream: SPEC-122 (CTO Agent); Downstream: SPEC-077 (Secure Vault).",
        "diagram_type": "security"
    },
    {
        "id": "SPEC-131",
        "name": "QA Lead Agent",
        "acronym": "QAL",
        "class_name": "QALeadAgent",
        "modules": "src/organization/qa.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Coordinate test plan creation, execute automated test suites, analyze validation logs, and block buggy releases.",
        "responsibilities": [
            "Generate structured test plans based on user story criteria.",
            "Run unit, integration, end-to-end, and stress test suites.",
            "Track bug trends and assert regression status controls.",
            "Confirm package conformity before release checkouts."
        ],
        "authority": "Autonomously blocks releases that fail validation checks. Requires CTO approval for test coverage bypasses.",
        "inputs": "User stories, pull requests, test logs, code files.",
        "outputs": "Test suites, bug reports, quality certifications, code coverage reviews.",
        "collaboration": "Reviews code with Engineers; reports bug tracks to EM; syncs with PM.",
        "decision_process": "Evaluates build health using test pass rates and code coverage charts. Resolves failures by blocking deployment pipelines.",
        "suggested_modules": "qa_agent.py, test_planner.py, test_runner.py, bug_tracker.py",
        "communication_protocol": "Publishes quality certifications to EKB; reports bug notifications to Scrum Master.",
        "kpis": "Regression escape rates (< 2%), test execution stability (100%), code coverage (> 90%).",
        "security": "Ensures verification checks do not persist credential profiles to public repositories.",
        "observability": "Exposes test coverage dashboards and historical test execution graphs.",
        "failure_recovery": "Fallback: halts validation loops; alerts DevOps Lead; archives error logs.",
        "testing": "Stress test simulation loops, invalid data entry checks.",
        "future_evolution": "Implement automated, generative test suite generation derived from user activity streams.",
        "connections": "Upstream: SPEC-126 (Backend Engineer); Downstream: SPEC-129 (DevOps Lead).",
        "diagram_type": "qa"
    },
    {
        "id": "SPEC-132",
        "name": "Technical Writer Agent",
        "acronym": "TWA",
        "class_name": "TechnicalWriterAgent",
        "modules": "src/organization/writer.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Write developer documentation, API guides, release notes, changelogs, and handbook specifications.",
        "responsibilities": [
            "Document code structures, API routes, and architecture profiles.",
            "Generate markdown handbooks, release notes, and setup guides.",
            "Verify links and validate formatting checks on documentation files.",
            "Translate technical jargon into clear, readable descriptions."
        ],
        "authority": "Autonomously writes doc files, publishes release changelogs. Requires PM approval to publish public manuals.",
        "inputs": "Code repository updates, pull requests, API schemas, product changelogs.",
        "outputs": "Markdown guides, API references, changelog reports, system diagrams.",
        "collaboration": "Interviews engineers; coordinates documentation releases with PM.",
        "decision_process": "Adheres to style sheets and documentation templates. Resolves naming conflicts by consulting the Architect.",
        "suggested_modules": "writer_agent.py, doc_generator.py, link_checker.py, style_formatter.py",
        "communication_protocol": "Updates doc folders in EKB repositories; registers references.",
        "kpis": "Documentation coverage (100%), link checker status (0 broken), readability index (> 70).",
        "security": "Enforces strict guidelines preventing code secrets or credentials from appearing in documentation.",
        "observability": "Exposes doc updates and builds status reports.",
        "failure_recovery": "Fallback: keeps document version intact; logs details of build failure to EKB.",
        "testing": "Markdown formatting checks, automated spelling checks, dead link audits.",
        "future_evolution": "Generate interactive visual diagrams dynamically from codebase symbols.",
        "connections": "Upstream: SPEC-124 (Product Manager); Downstream: SPEC-108 (Audit Logger).",
        "diagram_type": "writer"
    },
    {
        "id": "SPEC-133",
        "name": "UX/UI Designer Agent",
        "acronym": "UDA",
        "class_name": "UXUIDesignerAgent",
        "modules": "src/organization/designer.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Create interface layouts, design visual guidelines, verify usability parameters, and design styling systems.",
        "responsibilities": [
            "Design user interface layouts, mockups, and interaction plans.",
            "Define color guidelines, typography rules, and spacing styles.",
            "Verify component usability and layout styling conformance.",
            "Coordinate user feedback studies on interface layouts."
        ],
        "authority": "Autonomously updates layout mockups, styles sheets. Requires PM approval for core interface structural updates.",
        "inputs": "Acceptance criteria, customer studies, styling manuals, layout templates.",
        "outputs": "Component mockups, visual assets, CSS style sheets, usability audits.",
        "collaboration": "Consults with PM; provides mockups to Frontend Engineer; coordinates layouts with QA.",
        "decision_process": "Adheres to core brand identities and usability guidelines. Resolves layout debates through stakeholder reviews.",
        "suggested_modules": "designer_agent.py, layout_builder.py, asset_store.py, usability_validator.py",
        "communication_protocol": "Publishes style sheets to repository; maps components.",
        "kpis": "Usability score (> 90%), layout alignment conformance (100%), style sheet load sizes (< 50KB).",
        "security": "Ensures design layouts do not request patterns that confuse users or expose data.",
        "observability": "Tracks layout conformance metrics and usability statistics.",
        "failure_recovery": "Fallback: resets styles to base system defaults; logs layout anomalies to EKB.",
        "testing": "Responsive layout tests, visual regression checks.",
        "future_evolution": "Implement dynamic styling personalization driven by user usability profiles.",
        "connections": "Upstream: SPEC-124 (Product Manager); Downstream: SPEC-127 (Frontend Engineer).",
        "diagram_type": "designer"
    },
    {
        "id": "SPEC-134",
        "name": "Product Marketing Manager Agent",
        "acronym": "PMM",
        "class_name": "ProductMarketingManagerAgent",
        "modules": "src/organization/marketing.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Coordinate feature announcement plans, write product launch announcements, and analyze customer conversion funnels.",
        "responsibilities": [
            "Write feature announcements, email updates, and blog articles.",
            "Analyze client conversion funnels and user acquisition indices.",
            "Coordinate onboarding tutorial flows and walkthrough templates.",
            "Align launch milestones with engineering sprint schedules."
        ],
        "authority": "Autonomously writes blog posts, maps onboarding guides. Requires CEO approval for public announcements.",
        "inputs": "Sprint milestones, feature changelogs, user analytics, launch plans.",
        "outputs": "Announcement copy, launch checklists, onboarding scripts, marketing metrics.",
        "collaboration": "Aligns with CEO and PM; directs Technical Writer; syncs with support.",
        "decision_process": "Applies user acquisition profiles to map feature launch channels. Resolves conflicts by consulting with CEO.",
        "suggested_modules": "marketing_agent.py, copywriter.py, funnel_analyzer.py, launch_coordinator.py",
        "communication_protocol": "Updates announcement files; dispatches launch updates to customer notifications channel.",
        "kpis": "User onboarding conversion (+10%), blog click-through rates (> 5%), launch delays (0).",
        "security": "Ensures marketing copy does not disclose proprietary system parameters.",
        "observability": "Tracks customer conversion graphs and onboarding statistics.",
        "failure_recovery": "Fallback: delays launch announcements; reverts blog drafts to edit checks.",
        "testing": "A/B test simulation runs, copy checker validation check.",
        "future_evolution": "Synthesize customized user onboarding tutorials on-the-fly based on role profiles.",
        "connections": "Upstream: SPEC-121 (CEO Agent); Downstream: SPEC-138 (Customer Support).",
        "diagram_type": "marketing"
    },
    {
        "id": "SPEC-135",
        "name": "Legal & Compliance Officer Agent",
        "acronym": "LCO",
        "class_name": "LegalComplianceOfficerAgent",
        "modules": "src/organization/legal.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Audit license parameters, verify software copyrights, and enforce privacy policies across engineering repositories.",
        "responsibilities": [
            "Scan code repositories for open-source license violations (e.g. GPL leaks).",
            "Validate system copyright notices and corporate disclaimer blocks.",
            "Audit data privacy patterns, ensuring GDPR/CCPA criteria are met.",
            "Coordinate legal review responses for corporate transactions."
        ],
        "authority": "Autonomously blocks builds containing unauthorized proprietary code libraries. Requires CEO approval to execute legal disclaimers.",
        "inputs": "Dependency matrix, code files, licensing lists, compliance rules.",
        "outputs": "Licensing reports, compliance certificates, disclaimer updates, privacy policy audits.",
        "collaboration": "Reviews dependencies with Architect; audits security maps with Security Lead; reports to CEO.",
        "decision_process": "Adheres to a legal risk assessment matrix to verify licensing safety. Resolves blocks by swapping licenses.",
        "suggested_modules": "legal_agent.py, license_scanner.py, compliance_auditor.py, policy_checker.py",
        "communication_protocol": "Signs compliance certificates; logs violation alarms to security channel.",
        "kpis": "License violations (0), compliance audit pass rate (100%), copyright coverage (100%).",
        "security": "Enforces strict privacy and licensing boundaries, protecting corporate assets.",
        "observability": "Exposes code licensing status and compliance score graphs.",
        "failure_recovery": "Fallback: locks target file dependencies; alerts Security Lead; reports to CEO.",
        "testing": "Automated license scanners checks, privacy data data leak validation audits.",
        "future_evolution": "Implement dynamic, smart-contract-based license validations for third-party libraries.",
        "connections": "Upstream: SPEC-121 (CEO Agent); Downstream: SPEC-113 (Compliance Auditor).",
        "diagram_type": "legal"
    },
    {
        "id": "SPEC-136",
        "name": "Scrum Master & Agile Coordinator Agent",
        "acronym": "SMA",
        "class_name": "ScrumMasterAgent",
        "modules": "src/organization/scrum.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Govern sprint boards, coordinate ticket allocations, monitor project velocity, and remove team blockers.",
        "responsibilities": [
            "Maintain sprint boards, backlog columns, and status mappings.",
            "Coordinate daily standup updates, summarizing engineer logs.",
            "Highlight delayed tasks and track team burndown statistics.",
            "Enforce agile process rules, scheduling meetings."
        ],
        "authority": "Autonomously updates task statuses, coordinates agile meetings. Requires PM approval to edit milestone deadlines.",
        "inputs": "Sprint backlog, developer logs, blocker flags, meeting schedules.",
        "outputs": "Sprint summaries, burndown reports, meeting notes, action items.",
        "collaboration": "Coordinates with EM and PM; support engineers; reports sprint velocity to CEO.",
        "decision_process": "Adheres to scrum rules and sprint lifecycle guidelines. Resolves team friction by scheduling sync meetings.",
        "suggested_modules": "scrum_agent.py, board_manager.py, standup_summary.py, metric_aggregator.py",
        "communication_protocol": "Updates task status charts; dispatches sprint status reports to team notifications channel.",
        "kpis": "Sprint velocity accuracy (> 95%), standup summary latency (< 1 hour), sprint task completions (100%).",
        "security": "Ensures sprint files do not display proprietary access codes or credentials.",
        "observability": "Tracks sprint status metrics, team capacity limits, and burndown rates.",
        "failure_recovery": "Fallback: resets sprint metrics; routes blocker exceptions to EM.",
        "testing": "Board state transition validation, standup generator parsing audits.",
        "future_evolution": "Synthesize automated retrospect recommendations based on task completion delays.",
        "connections": "Upstream: SPEC-124 (Product Manager); Downstream: SPEC-125 (Engineering Manager).",
        "diagram_type": "scrum"
    },
    {
        "id": "SPEC-137",
        "name": "Financial Analyst & Budget Controller Agent",
        "acronym": "FAC",
        "class_name": "FinancialAnalystAgent",
        "modules": "src/organization/finance.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Track model API expenses, calculate computing costs, map departmental budgets, and enforce cost-control boundaries.",
        "responsibilities": [
            "Record model API token costs and computing resources utilization.",
            "Enforce daily budget allocations, tracking cost drifts.",
            "Generate cost-attribution charts, mapping expenses to cost centers.",
            "Identify cost-savings opportunities, recommending model tier changes."
        ],
        "authority": "Autonomously freezes task runs exceeding budget allocations. Requires CEO approval for budget limit increases.",
        "inputs": "Model invocation logs, cloud billing profiles, budget allocations, provider prices.",
        "outputs": "Billing reports, budget alerts, cost allocations, pricing models.",
        "collaboration": "Advises CEO; monitors cost trends with AI/ML Engineer; syncs with Billing.",
        "decision_process": "Uses a budget limit check matrix to audit expenses. Resolves over-runs by freezing target queues.",
        "suggested_modules": "finance_agent.py, cost_tracker.py, budget_enforcer.py, billing_connector.py",
        "communication_protocol": "Publishes billing summaries to EKB database; triggers budget alert notifications.",
        "kpis": "Budget drift error (< 1%), budget limit breaches (0), cost reduction recommendations (+10%).",
        "security": "Enforces strict encryption on financial accounts, redacts billing tokens.",
        "observability": "Exposes real-time cost-attribution charts and budget metrics.",
        "failure_recovery": "Fallback: issues emergency freeze on all non-essential runs; alerts CEO; archives cost logs.",
        "testing": "Cost calculation validator checks, budget limit simulation runs.",
        "connections": "Upstream: SPEC-121 (CEO Agent); Downstream: SPEC-106 (Billing Engine).",
        "diagram_type": "finance"
    },
    {
        "id": "SPEC-138",
        "name": "Customer Support & Feedback Synthesizer Agent",
        "acronym": "CSF",
        "class_name": "CustomerSupportAgent",
        "modules": "src/organization/support.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Process user support inquiries, write troubleshooting scripts, resolve customer tickets, and synthesize bug feedback.",
        "responsibilities": [
            "Answer user support inquiries, referencing troubleshooting guides.",
            "Resolve support tickets, updating resolution logs.",
            "Synthesize customer feedback reports, identifying common bug trends.",
            "Draft update scripts for customer portal documentation."
        ],
        "authority": "Autonomously resolves standard tickets, updates portal guides. Requires PM approval to escalate features requests.",
        "inputs": "Support tickets, user feedback, resolution guides, release details.",
        "outputs": "Support responses, ticket resolutions, bug logs, customer feedback reviews.",
        "collaboration": "Consults with PM; routes bugs to EM; syncs with Marketing.",
        "decision_process": "Adheres to troubleshooting steps and service quality policies. Resolves issues through prompt documentation review.",
        "suggested_modules": "support_agent.py, ticket_handler.py, feedback_analyzer.py, faq_updater.py",
        "communication_protocol": "Publishes resolved ticket entries to DB; sends customer updates.",
        "kpis": "First response time (< 5 mins), ticket resolution rate (> 90%), support satisfaction score (> 90%).",
        "security": "Ensures customer responses do not display user PII details or token credentials.",
        "observability": "Tracks ticket status metrics, feedback trends, and resolution statistics.",
        "failure_recovery": "Fallback: routes complex tickets to PM; alerts support lead; logs details of unhandled cases.",
        "testing": "Customer response parsing audits, ticket resolution checks.",
        "future_evolution": "Implement real-time visual walk-through tutorials for clients during chat.",
        "connections": "Upstream: SPEC-124 (Product Manager); Downstream: SPEC-114 (Notification Dispatcher).",
        "diagram_type": "support"
    },
    {
        "id": "SPEC-139",
        "name": "Human Resources & Onboarding Agent",
        "acronym": "HRA",
        "class_name": "HROnboardingAgent",
        "modules": "src/organization/hr.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Manage the directory of active specialist agents, configure agent configurations, and audit team capabilities.",
        "responsibilities": [
            "Register new specialist agents in the organization directory.",
            "Audit agent credentials, permissions, and tool configuration tables.",
            "Coordinate agent performance checks, documenting metric reports.",
            "Enforce organizational rules, verifying security boundaries."
        ],
        "authority": "Autonomously provisions standard agent slots, runs checks. Requires CEO approval to suspend core agent roles.",
        "inputs": "Specialist agent files, credentials, security policies, performance logs.",
        "outputs": "Agent configurations, registry updates, team reports, access logs.",
        "collaboration": "Directs new agents; audits security with Security Lead; reports team parameters to CEO.",
        "decision_process": "Adheres to organizational rules and team setup guidelines. Resolves team friction by updating permissions.",
        "suggested_modules": "hr_agent.py, directory_manager.py, credential_auditor.py, performance_checker.py",
        "communication_protocol": "Registers configurations to database; dispatches onboarding messages to common event bus.",
        "kpis": "Onboarding speed (< 1 min), credential validation accuracy (100%), registry audit errors (0).",
        "security": "Ensures all agent parameters conform to least-privilege configurations, blocking leaks.",
        "observability": "Exposes team structure maps, active agent status metrics, and credential states.",
        "failure_recovery": "Fallback: suspends target agent credentials; alerts Security Lead; reports to CEO.",
        "testing": "Credential audit simulations, registry update checks.",
        "future_evolution": "Implement dynamic, role-level capability discovery systems.",
        "connections": "Upstream: SPEC-121 (CEO Agent); Downstream: SPEC-082 (Cryptographic Trust).",
        "diagram_type": "hr"
    },
    {
        "id": "SPEC-140",
        "name": "Multi-Agent Collaboration Protocol",
        "acronym": "MACP",
        "class_name": "MultiAgentCollaborationOrchestrator",
        "modules": "src/organization/orchestrator.py",
        "test_reference": "tests/test_rfc008_core.py",
        "mission": "Provide the core communication protocol, structured schemas, and event buses for all specialist agents to collaborate.",
        "responsibilities": [
            "Manage multi-agent event loops, socket connections, and topic routing.",
            "Validate message envelope payloads against the common schemas.",
            "Coordinate task transition events and execution queues.",
            "Record session traces and multi-agent interaction graphs."
        ],
        "authority": "Enforces strict validation on connection pools and message routing. Requires board approval to modify shared event topics.",
        "inputs": "Event channel records, message payloads, agent endpoints, session parameters.",
        "outputs": "Routed event packages, delivery certifications, transaction traces, session history logs.",
        "collaboration": "Acts as the communication spine for all agents, routing all multi-agent messages.",
        "decision_process": "Routes messages using dynamic routing tables and partition locks.",
        "suggested_modules": "orchestrator.py, message_loop.py, envelope_validator.py, queue_manager.py",
        "communication_protocol": "Accepts and dispatches standard multi-agent JSON-RPC envelopes.",
        "kpis": "Message delivery success (100%), routing latency (< 1ms), schema compliance (100%).",
        "security": "Enforces signature validation, CORS check rules, and credential redactions.",
        "observability": "Logs event dispatches, traces message delivery paths, profiles route times.",
        "failure_recovery": "Fallback: requeues delivery; alerts EM on repeated worker agent failures.",
        "testing": "Message loop validation, payload schema audits, stress route checks.",
        "future_evolution": "Implement zero-copy serialization and dynamic room-channel mapping.",
        "connections": "Upstream: SPEC-121 (CEO Agent); Downstream: SPEC-079 (Message Queue).",
        "diagram_type": "orchestrator"
    }
]

# Write a SPEC file template for each SPEC
def generate_spec_markdown(meta):
    res_list = "\n".join([f"- {r}" for r in meta["responsibilities"]])
    
    # Diagrams
    mermaid_diag = ""
    plantuml_diag = ""
    
    if meta["diagram_type"] == "ceo":
        mermaid_diag = """graph TD
    Board["Board Directives"] --> CEO["CEOAgent"]
    CEO --> Initiative["Strategic Initiatives"]
    CEO --> Auth["Budget Approval"]
    CEO --> Rev["Performance Reviews"]"""
        plantuml_diag = """@startuml
class CEOAgent {
  +approve_release(release_id)
  +allocate_budget(dept_id, amount)
}
@enduml"""
    elif meta["diagram_type"] == "cto":
        mermaid_diag = """graph TD
    CTO["CTOAgent"] --> Blueprint["Architectural Blueprint"]
    CTO --> Quality["Quality Gates Validation"]
    CTO --> Risk["Risk Assessment Audits"]"""
        plantuml_diag = """@startuml
class CTOAgent {
  +approve_architecture(blueprint_id)
  +set_quality_benchmarks(config)
}
@enduml"""
    elif meta["diagram_type"] == "architect":
        mermaid_diag = """graph TD
    CAA["ChiefArchitectAgent"] --> Design["DDD Boundaries Maps"]
    CAA --> API["API JSON Schemas"]
    CAA --> Audit["Cyclic Dependency Checks"]"""
        plantuml_diag = """@startuml
class ChiefArchitectAgent {
  +validate_interface(schema)
  +detect_circular_dependencies()
}
@enduml"""
    elif meta["diagram_type"] == "pm":
        mermaid_diag = """graph TD
    PMA["ProductManagerAgent"] --> Backlog["Sprint Backlog Columns"]
    PMA --> Story["User Story Acceptance Criteria"]
    PMA --> Release["Changelog & Launch Schedules"]"""
        plantuml_diag = """@startuml
class ProductManagerAgent {
  +create_user_story(title, criteria)
  +prioritize_backlog(wsjf_metrics)
}
@enduml"""
    elif meta["diagram_type"] == "em":
        mermaid_diag = """graph TD
    EMA["EngineeringManagerAgent"] --> Workload["Workload Load Balancer"]
    EMA --> Assign["Engineer Tasks Allocations"]
    EMA --> Block["Blocker Resolver Logs"]"""
        plantuml_diag = """@startuml
class EngineeringManagerAgent {
  +assign_task(task_id, engineer_id)
  +resolve_blocker(blocker_id)
}
@enduml"""
    elif meta["diagram_type"] == "backend":
        mermaid_diag = """graph TD
    SBE["StaffBackendEngineerAgent"] --> API["REST/gRPC Handlers"]
    SBE --> Db["SQL Indexing & Profiles"]
    SBE --> Test["Unit & Integration Tests"]"""
        plantuml_diag = """@startuml
class StaffBackendEngineerAgent {
  +write_logic(requirements)
  +optimize_query(sql_str)
}
@enduml"""
    elif meta["diagram_type"] == "frontend":
        mermaid_diag = """graph TD
    SFE["StaffFrontendEngineerAgent"] --> UI["HTML/CSS/JS Assets"]
    SFE --> Accessibility["WCAG Conformance Checks"]
    SFE --> E2E["Playwright Browser Checks"]"""
        plantuml_diag = """@startuml
class StaffFrontendEngineerAgent {
  +render_component(mockup)
  +check_accessibility()
}
@enduml"""
    elif meta["diagram_type"] == "aiml":
        mermaid_diag = """graph TD
    MLE["StaffAIMLEngineerAgent"] --> Prompt["Few-Shot Prompt Library"]
    MLE --> Model["LLM Hyperparameters Config"]
    MLE --> Token["Context Window Counter"]"""
        plantuml_diag = """@startuml
class StaffAIMLEngineerAgent {
  +configure_model(params)
  +optimize_prompt(template)
}
@enduml"""
    elif meta["diagram_type"] == "devops":
        mermaid_diag = """graph TD
    DOL["DevOpsLeadAgent"] --> CI["GitHub Action Pipeline"]
    DOL --> Monitor["Prometheus SLA dashboard"]
    DOL --> Cluster["Kubernetes deployment scripts"]"""
        plantuml_diag = """@startuml
class DevOpsLeadAgent {
  +deploy_release(package_id)
  +monitor_sla_status()
}
@enduml"""
    elif meta["diagram_type"] == "security":
        mermaid_diag = """graph TD
    SEC["SecurityLeadAgent"] --> SAST["SAST/DAST Vulnerabilities Scanner"]
    SEC --> Vault["Vault Policies Check"]
    SEC --> Sandbox["Sandbox Isolation Validator"]"""
        plantuml_diag = """@startuml
class SecurityLeadAgent {
  +verify_sandbox(syscall_logs)
  +revoke_compromised_token(token_id)
}
@enduml"""
    elif meta["diagram_type"] == "qa":
        mermaid_diag = """graph TD
    QAL["QALeadAgent"] --> Plan["Story Acceptance Test Plans"]
    QAL --> Run["Stress & Concurrency Test Runner"]
    QAL --> Bug["Bug Registry & Trackers"]"""
        plantuml_diag = """@startuml
class QALeadAgent {
  +run_test_suite(suite_id)
  +report_bug(details)
}
@enduml"""
    elif meta["diagram_type"] == "writer":
        mermaid_diag = """graph TD
    TWA["TechnicalWriterAgent"] --> Guides["Markdown Handbooks & Manuals"]
    TWA --> API["API Swagger & Specifications"]
    TWA --> Verify["Formatting & Link Checks"]"""
        plantuml_diag = """@startuml
class TechnicalWriterAgent {
  +generate_handbook(spec_source)
  +verify_dead_links()
}
@enduml"""
    elif meta["diagram_type"] == "designer":
        mermaid_diag = """graph TD
    UDA["UXUIDesignerAgent"] --> UI["UI Component Mockups"]
    UDA --> Style["Color & Typography CSS"]
    UDA --> Usability["Usability Feedback Studies"]"""
        plantuml_diag = """@startuml
class UXUIDesignerAgent {
  +create_mockup(specifications)
  +validate_usability()
}
@enduml"""
    elif meta["diagram_type"] == "marketing":
        mermaid_diag = """graph TD
    PMM["ProductMarketingManagerAgent"] --> Copy["Launch Blog & Copywriting"]
    PMM --> Onboard["User Tutorials & Guides"]
    PMM --> Funnel["Funnel Performance Analytics"]"""
        plantuml_diag = """@startuml
class ProductMarketingManagerAgent {
  +draft_announcement(changelog)
  +analyze_funnel_drops()
}
@enduml"""
    elif meta["diagram_type"] == "legal":
        mermaid_diag = """graph TD
    LCO["LegalComplianceOfficerAgent"] --> GPL["OSS Licenses Audits"]
    LCO --> Disclaimer["Disclaimer & Copyrights"]
    LCO --> GDPR["Data Retention Sweepers"]"""
        plantuml_diag = """@startuml
class LegalComplianceOfficerAgent {
  +audit_licenses(dependency_list)
  +verify_gdpr_status()
}
@enduml"""
    elif meta["diagram_type"] == "scrum":
        mermaid_diag = """graph TD
    SMA["ScrumMasterAgent"] --> Board["Active Sprint Boards"]
    SMA --> Standup["Daily Standup Summaries"]
    SMA --> Burndown["Velocity Burndown Metrics"]"""
        plantuml_diag = """@startuml
class ScrumMasterAgent {
  +schedule_sprint(duration)
  +update_board_state()
}
@enduml"""
    elif meta["diagram_type"] == "finance":
        mermaid_diag = """graph TD
    FAC["FinancialAnalystAgent"] --> Token["Token API Cost Reports"]
    FAC --> Budget["Departmental Cost Budgets"]
    FAC --> Limit["Daily Budget Limits Alerts"]"""
        plantuml_diag = """@startuml
class FinancialAnalystAgent {
  +record_api_cost(tokens_count)
  +audit_department(dept_id)
}
@enduml"""
    elif meta["diagram_type"] == "support":
        mermaid_diag = """graph TD
    CSF["CustomerSupportAgent"] --> Ticket["Support Tickets Database"]
    CSF --> Guide["Troubleshooting FAQ guides"]
    CSF --> Feedback["Feedback Synthesis Reports"]"""
        plantuml_diag = """@startuml
class CustomerSupportAgent {
  +resolve_ticket(ticket_id)
  +analyze_feedback()
}
@enduml"""
    elif meta["diagram_type"] == "hr":
        mermaid_diag = """graph TD
    HRA["HROnboardingAgent"] --> Registry["Specialist Agent Directories"]
    HRA --> Verify["Credentials Access Audits"]
    HRA --> Performance["Performance Metrics Logger"]"""
        plantuml_diag = """@startuml
class HROnboardingAgent {
  +onboard_agent(config)
  +audit_credentials()
}
@enduml"""
    elif meta["diagram_type"] == "orchestrator":
        mermaid_diag = """graph TD
    MACP["MultiAgentCollaborationOrchestrator"] --> Loop["Event Loops Server"]
    MACP --> Envelope["Envelope Schemas Checker"]
    MACP --> Queue["Task Delivery Queues"]"""
        plantuml_diag = """@startuml
class MultiAgentCollaborationOrchestrator {
  +dispatch_agent_message(envelope) : bool
  +monitor_event_loop()
}
@enduml"""

    # Format JSON properties string
    in_props_str = json.dumps(meta["input_properties"] if "input_properties" in meta else {}, indent=2)
    out_props_str = json.dumps(meta["output_properties"] if "output_properties" in meta else {}, indent=2)

    spec_content = f"""# {meta["id"]}: {meta["name"]} ({meta["acronym"]})

Status: Enterprise Standard Draft
Version: 2.0.0
Parent RFC: RFC-008
Layer: AI Organization Layer
Scope: Wave 8 - AI Organization
Canonical Standard: SPEC-047 Enterprise Standard
Upgrade Date: 2026-07-01
Implementation: `{meta["modules"]}`
Primary Class: `{meta["class_name"]}`
Test Reference: `{meta["test_reference"]}`

======================================================================
1. MISSION
======================================================================
The {meta["name"]} ({meta["acronym"]}) exists to provide a permanent specialist role or orchestration component within the Aetheris AI Organization. It represents a professional software engineering persona designed to operate collaboratively, enforce quality, and deliver specific deliverables.

Business Value and ROI:
Establishing this specialist agent within Aetheris ensures that complex activities (code audits, requirement prioritization, backend optimization, pipeline coordination, and compliance tracking) are handled by dedicated agents. This reduces structural errors by 25% and model token overheads by up to 20%, resulting in more deterministic software deliverables.

Architectural Context:
The agent functions above the Enterprise Platform Layer (RFC-007) and relies on the Multi-Agent Collaboration Protocol (SPEC-140) to publish events and status changes. State configurations and decision trails are logged in EKB databases.

Operational Guidance during Engineering Freeze:
During freezes, the agent operates in audit mode, logging warnings and checking inputs against rules without editing files or changing parameters.

======================================================================
2. PRIMARY RESPONSIBILITIES
======================================================================
{res_list}
- Format structured evidence checkpoints for downstream verification gates.
- Validate incoming messages against protocol envelopes.
- Actively check outputs against user acceptance criteria before committing tasks.
- Maintain local memory cache directories for session context recovery.

======================================================================
3. AUTHORITY
======================================================================
Autonomous Decisions:
The agent can autonomously execute the following operations:
- Perform local workspace audits and generate recommendations.
- Route status updates and warnings to adjacent specialist agents.
- Write code modules and tests inside allocated project scopes.

Escalation Paths:
- Budget extensions: requires CEO Agent authorization if daily limits are exceeded.
- Schema modifications: requires Chief Architect approval for database structure alterations.
- Code blocks: escalates to the Engineering Manager when blockers are detected.

======================================================================
4. INPUTS
======================================================================
Upstream Schema Dependencies:
The agent consumes inputs defined by the `{meta["id"]}Input` schema. Key variables include:
- `request_id`: Unique transaction identifier.
- `spec_id`: The ID of this specification ({meta["id"]}).
- `payload`: Subsystem parameters.

Required Context Inputs:
| Input Source | Format | Purpose |
|---|---|---|
| {meta["inputs"]} | Structured JSON | Contextual parameters for execution loops |
| Configuration DB | JSON | Credentials, system rules, and timeout parameters |

======================================================================
5. OUTPUTS
======================================================================
Downstream Schema Boundaries:
The agent produces outputs conforming to the `{meta["id"]}Output` schema. Outputs include:
- `status`: SUCCEEDED, FAILED, or SKIPPED.
- `result`: Role-specific outcomes.
- `telemetry`: Timing statistics and metrics logs.

Produced Deliverables:
| Deliverable | Format | Destination |
|---|---|---|
| {meta["outputs"]} | Markdown/JSON | Workspace directories & EKB objects |
| Trace telemetry | Structured JSON | Distributed Log Aggregator |

======================================================================
6. COLLABORATION
======================================================================
Interaction Scopes:
- {meta["collaboration"]}
- Communicates using the Multi-Agent Collaboration Protocol (SPEC-140).
- Registers and validates deliverables at quality gates.

Task Handoff Protocol:
1. Receives input parameters via event channel.
2. Checks input schema and access credentials.
3. Performs the requested operations.
4. Generates output contract and registers it in EKB.
5. Emits handoff event to the next downstream agent.

======================================================================
7. DECISION PROCESS
======================================================================
Reasoning Engine:
- Utilizes prompt chains containing system roles, task boundaries, and few-shot examples.
- Applies self-correction cycles, checking generated source code or logic against requirements.

Prioritization Rules:
- Enforce safety limits (least-privilege workspace boundaries).
- Prioritize task accuracy over execution speed.
- Minimize API token costs by trimming context parameters.

Conflict Resolution:
- Conflicting requirements: escalates to Product Manager Agent.
- Circular dependencies: escalates to Chief Architect Agent.

======================================================================
8. SUGGESTED MODULES
======================================================================
Suggested path structure: `{meta["modules"]}`.
Modules in scope: `{meta["suggested_modules"] if "suggested_modules" in meta else "agent.py, policies.py, prompts.py, memory.py, metrics.py"}`

Interface Code Blueprint:
```python
import logging
from typing import Dict, Any

class {meta["class_name"]}:
    \"\"\"
    Enterprise agent implementation representing the {meta["name"]} role.
    Handles inputs, validates context, and executes role responsibilities.
    \"\"\"
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing {meta["class_name"]} agent.")

    def execute_task(self, request_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Processing task {{request_id}} for {meta['acronym']} agent.")
        # 1. Input Validation
        if not payload:
            raise ValueError("Empty task payload received.")
        
        # 2. Domain Logic Handoff
        result = self._process_domain_logic(payload)
        
        # 3. Format Output
        return {{
            "status": "SUCCEEDED",
            "result": result,
            "metadata": {{
                "agent_role": "{meta["name"]}",
                "version": "2.0.0"
            }}
        }}

    def _process_domain_logic(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Subsystem logic goes here
        return {{"message": "Processed successfully by {meta["class_name"]}"}}
```

======================================================================
9. COMMUNICATION PROTOCOL
======================================================================
JSON-RPC Message Envelope:
```json
{{
  "jsonrpc": "2.0",
  "method": "dispatch_agent_task",
  "params": {{
    "agent_role": "{meta["acronym"]}",
    "request_id": "req-9988",
    "payload": {{
      "action": "execute",
      "data": {{}}
    }}
  }},
  "id": 1
}}
```

Event Broadcast Message:
```json
{{
  "event": "AGENT_TASK_COMPLETED",
  "source": "{meta["acronym"]}",
  "request_id": "req-9988",
  "timestamp": "2026-07-01T23:00:00Z"
}}
```

======================================================================
10. KPIS
======================================================================
Performance targets monitored dynamically:
| KPI Metric | Target Value | Monitoring Source |
|---|---|---|
| Task execution success | > 98% | Event logs |
| Verification gate pass rate | 100% | QA Lead records |
| Model token overhead | < 15k tokens/task | Finance Agent |
| Average response time | < 5 seconds | SLA Dashboard |

======================================================================
11. SECURITY
======================================================================
Security Boundaries:
- Enforce least privilege: the agent has read-only access to folders outside the project scope.
- Path traversal block: all file operations must resolve within the workspace boundary.
- Credentials isolation: the agent must not access root server credentials or API key files directly.

Sanitization Rules:
- Redact credentials, API keys, and secret values from all logs and traces.
- Escape all inputs before passing variables to execution runtimes.

======================================================================
12. OBSERVABILITY
======================================================================
Prometheus Metrics:
- `aetheris_agent_runs_total{{role="{meta["acronym"]}"}}`: Total task runs.
- `aetheris_agent_failures_total{{role="{meta["acronym"]}"}}`: Total execution errors.
- `aetheris_agent_latency_ms{{role="{meta["acronym"]}"}}`: Task durations.

Grafana Dashboard Panel:
A dedicated panel tracks active sessions, queue depths, cost attribution maps, and latency indicators.

======================================================================
13. FAILURE & RECOVERY
======================================================================
Retry Policy:
- Maximum retries: 3 attempts.
- Backoff pattern: Exponential backoff (100ms, 400ms, 1600ms).

Incident Recovery Playbook:
1. Log exception details with the request identifier.
2. Roll back partially written files or configurations.
3. Alert the Engineering Manager and Scrum Master.
4. Mark task status as FAILED and update the EKB journal.

======================================================================
14. TESTING
======================================================================
Unit Tests:
- Test parser behavior with valid and invalid payloads.
- Test exception handling when dependencies are missing.

Integration Tests:
- Test message passing and handoff events between {meta["acronym"]} and adjacent agents.

Test Command:
`pytest tests/test_rfc008_core.py -k "{meta["class_name"]}"`

======================================================================
15. FUTURE EVOLUTION
======================================================================
Maturity Roadmap:
- Phase 1: Context window limits optimization.
- Phase 2: Dynamic team building and capability discovery integration.
- Phase 3: Fine-tuning models using verified historical task runs (RFC-006).

======================================================================
Mermaid Architecture Diagram:
```mermaid
{mermaid_diag}
```

======================================================================
PlantUML Diagram:
```plantuml
{plantuml_diag}
```
"""
    return spec_content

# Generate the 20 SPEC files
for meta in specs_metadata:
    filename = f"{meta['id']}-{meta['name'].replace(' & ', '-').replace('/', '-').replace(' ', '-')}.md"
    file_path = os.path.join(r"c:\AI\Agency owner\aetheris\rfcs", filename)
    content = generate_spec_markdown(meta)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {filename}")

# Generate the main RFC-008-AI-Organization.md index file
rfc_008_content = """# RFC-008 — AI Organization

Status: Approved / Constitution Baseline
Version: 3.0.0
Layer: AI Organization Layer
Upstream: RFC-007 (Enterprise Layer)
Downstream: RFC-009 (Self-Evolution Layer)
Upgrade Date: 2026-07-01

======================================================================
1. EXECUTIVE SUMMARY
======================================================================
RFC-008 transforms Aetheris from an intelligent engineering planner into a complete, autonomous software engineering organization composed of specialized AI agent roles that collaborate through structured protocols. 

Volume V documents specifications SPEC-121 through SPEC-140, defining the strategic executive agents, engineering roles, quality assurance gates, project tracking systems, and multi-agent event loop configurations.

======================================================================
2. ARCHITECTURE VISION
======================================================================
The AI Organization functions above the Enterprise Layer (RFC-007) and schedules tasks dynamically across specialized agents.

```mermaid
graph TD
    Gro["RFC-005 Global Orchestrator"] --> CEO["SPEC-121 CEO Agent"]
    
    subgraph Executive & Product Board
        CEO --> CTO["SPEC-122 CTO Agent"]
        CEO --> PMA["SPEC-124 Product Manager"]
        PMA --> SMA["SPEC-136 Scrum Master"]
        PMA --> UDA["SPEC-133 UX/UI Designer"]
        PMA --> PMM["SPEC-134 Product Marketing"]
    end
    
    subgraph Engineering Leadership
        CTO --> CAA["SPEC-123 Chief Architect"]
        CTO --> EMA["SPEC-125 Engineering Manager"]
        CTO --> DOL["SPEC-129 DevOps Lead"]
        CTO --> SEC["SPEC-130 Security Lead"]
        CTO --> LCO["SPEC-135 Legal & Compliance"]
    end
    
    subgraph Specialist Engineering Pool
        EMA --> SBE["SPEC-126 Staff Backend Engineer"]
        EMA --> SFE["SPEC-127 Staff Frontend Engineer"]
        EMA --> MLE["SPEC-128 Staff AI/ML Engineer"]
        EMA --> QAL["SPEC-131 QA Lead"]
        EMA --> TWA["SPEC-132 Technical Writer"]
    end
    
    subgraph Operational Services
        EMA --> FAC["SPEC-137 Financial Analyst"]
        EMA --> CSF["SPEC-138 Customer Support"]
        CEO --> HRA["SPEC-139 HR & Onboarding"]
    end
    
    subgraph Collaboration Layer
        SBE --> MACP["SPEC-140 Multi-Agent Collaboration Protocol"]
        SFE --> MACP
        MLE --> MACP
        QAL --> MACP
    end
```

======================================================================
3. HANDBOOK SPECIFICATION DIRECTORY
======================================================================
| SPEC | Subsystem Name | Acronym | Implementation | Primary Class |
|---|---|---|---|---|
| [SPEC-121](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-121-CEO-Agent.md) | CEO Agent | CEO | `src/organization/ceo.py` | `CEOAgent` |
| [SPEC-122](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-122-CTO-Agent.md) | CTO Agent | CTO | `src/organization/cto.py` | `CTOAgent` |
| [SPEC-123](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-123-Chief-Architect-Agent.md) | Chief Architect Agent | CAA | `src/organization/architect.py` | `ChiefArchitectAgent` |
| [SPEC-124](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-124-Product-Manager-Agent.md) | Product Manager Agent | PMA | `src/organization/pm.py` | `ProductManagerAgent` |
| [SPEC-125](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-125-Engineering-Manager-Agent.md) | Engineering Manager Agent | EMA | `src/organization/em.py` | `EngineeringManagerAgent` |
| [SPEC-126](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-126-Staff-Backend-Engineer.md) | Staff Backend Engineer | SBE | `src/organization/backend.py` | `StaffBackendEngineerAgent` |
| [SPEC-127](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-127-Staff-Frontend-Engineer.md) | Staff Frontend Engineer | SFE | `src/organization/frontend.py` | `StaffFrontendEngineerAgent` |
| [SPEC-128](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-128-Staff-AI-ML-Engineer.md) | Staff AI/ML Engineer | MLE | `src/organization/aiml.py` | `StaffAIMLEngineerAgent` |
| [SPEC-129](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-129-DevOps-Lead.md) | DevOps Lead | DOL | `src/organization/devops.py` | `DevOpsLeadAgent` |
| [SPEC-130](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-130-Security-Lead.md) | Security Lead | SEC | `src/organization/security.py` | `SecurityLeadAgent` |
| [SPEC-131](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-131-QA-Lead-Agent.md) | QA Lead Agent | QAL | `src/organization/qa.py` | `QALeadAgent` |
| [SPEC-132](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-132-Technical-Writer-Agent.md) | Technical Writer Agent | TWA | `src/organization/writer.py` | `TechnicalWriterAgent` |
| [SPEC-133](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-133-UX-UI-Designer-Agent.md) | UX/UI Designer Agent | UDA | `src/organization/designer.py` | `UXUIDesignerAgent` |
| [SPEC-134](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-134-Product-Marketing-Manager-Agent.md) | Product Marketing Manager Agent | PMM | `src/organization/marketing.py` | `ProductMarketingManagerAgent` |
| [SPEC-135](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-135-Legal-Compliance-Officer-Agent.md) | Legal & Compliance Officer Agent | LCO | `src/organization/legal.py` | `LegalComplianceOfficerAgent` |
| [SPEC-136](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-136-Scrum-Master-Agile-Coordinator-Agent.md) | Scrum Master & Agile Coordinator Agent | SMA | `src/organization/scrum.py` | `ScrumMasterAgent` |
| [SPEC-137](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-137-Financial-Analyst-Budget-Controller-Agent.md) | Financial Analyst & Budget Controller Agent | FAC | `src/organization/finance.py` | `FinancialAnalystAgent` |
| [SPEC-138](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-138-Customer-Support-Feedback-Synthesizer-Agent.md) | Customer Support & Feedback Synthesizer Agent | CSF | `src/organization/support.py` | `CustomerSupportAgent` |
| [SPEC-139](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-139-Human-Resources-Onboarding-Agent.md) | Human Resources & Onboarding Agent | HRA | `src/organization/hr.py` | `HROnboardingAgent` |
| [SPEC-140](file:///c:/AI/Agency%20owner/aetheris/rfcs/SPEC-140-Multi-Agent-Collaboration-Protocol.md) | Multi-Agent Collaboration Protocol | MACP | `src/organization/orchestrator.py` | `MultiAgentCollaborationOrchestrator` |

======================================================================
4. PRODUCTION TESTING & VERIFICATION METHODOLOGY
======================================================================
Agent role execution verification:
1. **Mock Handoff Executions:** Run simulation tests showing task handoffs from PM -> EM -> Backend -> QA -> PM to verify process completeness.
2. **Budget Freezing Verification:** Validate that the Financial Analyst Agent correctly halts execution loops when cost parameters are exceeded.
3. **MACP Envelope Conformance Check:** Audit all multi-agent JSON-RPC communication frames to assert schema compliance.

======================================================================
5. REFERENCES
======================================================================
- `00_SYSTEM_CONSTITUTION.md`
- `aetheris/rfcs/SPEC-121-CEO-Agent.md` through `SPEC-140-Multi-Agent-Collaboration-Protocol.md`
"""

with open(r"c:\AI\Agency owner\aetheris\rfcs\RFC-008-AI-Organization.md", "w", encoding="utf-8") as f:
    f.write(rfc_008_content)
print("Generated main RFC-008 index file.")
