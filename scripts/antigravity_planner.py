import os
import sys
import re
import json
import argparse
from pathlib import Path

# Paths Setup
WORKSPACE_DIR = Path(__file__).parent.parent.parent.resolve()
AETHERIS_DIR = WORKSPACE_DIR / "aetheris"
WEB_DIR = AETHERIS_DIR / "web"
PUBLIC_DIR = WEB_DIR / "public"

# Import compile_repo helpers if possible, else define inline
try:
    sys.path.insert(0, str(AETHERIS_DIR / "scripts"))
    import compile_repo
except ImportError:
    compile_repo = None

def get_divisions():
    div_file = WORKSPACE_DIR / "divisions.json"
    if div_file.exists():
        with open(div_file, "r", encoding="utf-8") as f:
            return json.load(f).get("divisions", {})
    return {}

def analyze_domain(project_desc):
    """
    Score and select active divisions based on project description keywords.
    """
    desc_lower = project_desc.lower()
    active_divs = set()
    
    # Standard template matcher
    if any(k in desc_lower for k in ["e-commerce", "ecommerce", "shop", "store", "buy", "cart", "checkout"]):
        active_divs.update(["product", "strategy", "engineering", "design", "security", "integrations", "marketing", "sales", "finance", "project-management", "support", "scripts"])
    elif any(k in desc_lower for k in ["saas", "dashboard", "b2b", "subscription", "cloud", "multi-tenant"]):
        active_divs.update(["engineering", "product", "security", "integrations", "finance", "marketing", "strategy", "support", "project-management"])
    elif any(k in desc_lower for k in ["mobile", "app", "ios", "android", "phone", "tablet"]):
        active_divs.update(["design", "engineering", "product", "integrations", "security", "marketing"])
    elif any(k in desc_lower for k in ["ai", "model", "llm", "intelligence", "agent", "deep learning"]):
        active_divs.update(["aetheris", "engineering", "specialized", "integrations", "security", "strategy", "product"])
    else:
        # Fallback keyword matching
        divisions = get_divisions()
        for div_id in divisions.keys():
            if div_id in desc_lower or div_id.replace("-", "") in desc_lower:
                active_divs.add(div_id)
        # Minimum active divisions
        if not active_divs:
            active_divs.update(["engineering", "product", "project-management", "design"])
            
    return list(active_divs)

def map_skills(active_divs, all_skills):
    """
    Select and rank specific skills within the active divisions.
    """
    selected_skills = []
    for skill_id, skill in all_skills.items():
        if skill.get("division") in active_divs or skill.get("type") == "core":
            selected_skills.append(skill)
            
    # Rank skills by type (core first, then alphabetical)
    selected_skills.sort(key=lambda s: (0 if s.get("type") == "core" else 1, s.get("name")))
    return selected_skills

def generate_plan_markdown(project_name, active_divs, selected_skills, rfcs, specs):
    """
    Generate the full 10-chapter implementation plan.
    """
    div_names = ", ".join([d.title() for d in active_divs])
    skill_names = ", ".join([s["name"] for s in selected_skills[:12]]) + "..."
    
    # Custom details based on project type
    db_table = "users, products, orders, payments" if "commerce" in project_name.lower() else "accounts, subscriptions, metrics, logs"
    api_route = "/api/v1/checkout" if "commerce" in project_name.lower() else "/api/v1/auth/login"
    
    md = f"""# Engineering Implementation Plan — {project_name}

Generated dynamically by **AntiGravity Master Orchestrator** on behalf of Aetheris.

* **Departments Activated**: {div_names}
* **Orchestrated Specialists**: {skill_names}
* **Subsystem RFCs**: {", ".join(rfcs[:5])}
* **Contracts Mapping**: {", ".join(specs[:8])}...

---

## 1. Requirement Analysis
* **Functional Requirements**:
  * Implement core business services matching active modules.
  * Provide dynamic interface updates based on state machine changes.
  * Enable multi-tenant data segmentation and access control.
* **Non-Functional Requirements**:
  * Sub-100ms response times for all API interfaces.
  * 99.9% system availability via container clustering.
  * Full accessibility compliance meeting WCAG AA rules.
* **Risks & Assumptions**:
  * Assumes standard model APIs remain online.
  * Risk of rate-limiting on third-party payment/analytic endpoints.
* **Acceptance Criteria**:
  * All unit, integration, and E2E test suites must pass.
  * Security check validates zero hardcoded secrets.

---

## 2. Product Discovery (PRD)
* **User Stories**:
  * *As a Tenant Manager*, I want to create a workspace and define member roles so we can collaborate securely.
  * *As an End User*, I want to complete my core flow (checkout/login) in less than three clicks.
* **User Personas**:
  * **Architect Alice**: Needs to inspect schemas and dependency graphs.
  * **Operator Owen**: Needs clean logs, telemetry, and health check routes.
* **Success Metrics**:
  * Conversion rate, first-action latency, and daily active workspace count.

---

## 3. UI/UX Planning
* **Design System**:
  * Fonts: Inter (sans-serif), JetBrains Mono (code).
  * Color tokens: slate dark backgrounds (`#0a0b10`), active neon borders.
* **Component Strategy**:
  * Reusable glass-cards, status bars, and floating navigations.
* **Accessibility Plan**:
  * Aria-labels on all buttons, clear focus states, contrast ratio 4.5:1.

### UI Flow Chart (Mermaid)
```mermaid
graph TD
  Start[Landing Page] --> Login[Authenticate]
  Login --> Dashboard[Workspace Console]
  Dashboard --> Action[Perform Core Operations]
  Action --> Complete[Success Screen]
```

---

## 4. Database Design
* **Normalized Schema**:
  * Uses 3NF relationship mapping.
  * Tables: {db_table}, settings.
* **Indexes**:
  * B-Tree index on primary IDs and email lookups.

### Database ERD (Mermaid)
```mermaid
erDiagram
  ORGANIZATION ||--o{{ USER : contains
  USER ||--o{{ SESSION : creates
  USER ||--o{{ TRANSACTION : triggers
```

---

## 5. Backend Architecture
* **Clean Architecture**:
  * Separation of Core Entities, Use Cases, Controller Adapters, and Storage engines.
* **Core API Endpoints**:
  * `POST {api_route}` (payload validation)
  * `GET /api/v1/health` (live telemetry status)

---

## 6. Security Review
* **STRIDE Threat Analysis**:
  * *Spoofing*: Mitigated by secure HTTP-only session tokens.
  * *Tampering*: Validated via SHA-256 payload checksums.
* **Role-Based Access (RBAC)**:
  * Admins (Write/Delete), Members (Read/Write), Viewers (Read-only).

---

## 7. Integration Plan
* **Third-Party APIs**:
  * Stripe Gateway: Payment rails.
  * SendGrid: Webhook notifications.
  * Auth0: Federated single sign-on.

---

## 8. DevOps & Deployment
* **Container Environment**:
  * Multi-stage Dockerfile compiling assets, and docker-compose orchestration.
* **Reverse Proxy**:
  * Nginx proxy directing traffic to backend with automated SSL certificates.

---

## 9. Testing Strategy
* **Unit Testing**:
  * Testing core mock classes using pytest.
* **Performance Testing**:
  * Benchmarking payload sizes and request concurrency limits.

---

## 10. Documentation Handbook
* **Developer Onboarding**:
  1. Clone repository.
  2. Setup environment variables (`.env`).
  3. Run `npm install` and `npm run dev`.
"""
    return md

def main():
    parser = argparse.ArgumentParser(description="AntiGravity Dynamic Skill Orchestrator CLI")
    parser.add_argument("--project", type=str, required=True, help="Description of the project to plan")
    parser.add_argument("--output", type=str, default="plans", help="Output directory inside workspace")
    args = parser.parse_args()
    
    print(f"AntiGravity Orchestrator starting planning loop for: '{args.project}'...")
    
    # Load all compiled data
    db_file = PUBLIC_DIR / "data.json"
    if not db_file.exists():
        print(f"Error: Aetheris database data.json not found. Run compile_repo.py first.")
        sys.exit(1)
        
    with open(db_file, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    skills = db.get("skills", {})
    rfcs_dict = db.get("rfcs", {})
    specs_dict = db.get("specs", {})
    
    # 1. Analyze domain and select divisions
    active_divs = analyze_domain(args.project)
    print(f"  Activated divisions: {', '.join(active_divs)}")
    
    # 2. Map skills
    selected_skills = map_skills(active_divs, skills)
    print(f"  Selected {len(selected_skills)} specialized skills.")
    
    # 3. Match RFCs and SPECs
    matched_rfcs = []
    matched_specs = []
    
    # Match based on selected skills' relationships
    for skill in selected_skills:
        for rfc in skill.get("related_rfcs", []):
            if rfc in rfcs_dict and rfc not in matched_rfcs:
                matched_rfcs.append(rfc)
        for spec in skill.get("related_specs", []):
            if spec in specs_dict and spec not in matched_specs:
                matched_specs.append(spec)
                
    # Minimum specs if none matched
    if not matched_specs:
        matched_specs = list(specs_dict.keys())[:10]
    if not matched_rfcs:
        matched_rfcs = list(rfcs_dict.keys())[:3]
        
    print(f"  Mapped {len(matched_rfcs)} RFCs and {len(matched_specs)} SPECs.")
    
    # Generate implementation plan text
    project_slug = compile_repo.slugify(args.project) if compile_repo else args.project.lower().replace(" ", "-")
    plan_md = generate_plan_markdown(args.project, active_divs, selected_skills, matched_rfcs, matched_specs)
    
    # Write outputs
    output_dir = WORKSPACE_DIR / args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_path = output_dir / f"{project_slug}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(plan_md)
        
    # Write JSON metadata representation
    plan_json = {
        "project": args.project,
        "slug": project_slug,
        "divisions": active_divs,
        "skills": [s["id"] for s in selected_skills],
        "rfcs": matched_rfcs,
        "specs": matched_specs,
        "content": plan_md
    }
    
    json_path = output_dir / f"{project_slug}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(plan_json, f, indent=2)
        
    print(f"SUCCESS: Generated implementation plan written to:")
    print(f"  - Markdown: {md_path}")
    print(f"  - JSON: {json_path}")

if __name__ == "__main__":
    main()
