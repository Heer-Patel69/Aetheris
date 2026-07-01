import os
import json
import time
from pathlib import Path
from typing import List, Dict, Set

# Event Bus interface
try:
    from kernel.event_bus import EventBus
except ImportError:
    class EventBus:
        def __init__(self, workspace_path, telemetry=None):
            self.workspace_path = workspace_path
        def publish(self, event_type, publisher, payload, priority="NORMAL"):
            pass

class PromptNormalizer:
    """Sanitizes raw user prompt text."""
    @staticmethod
    def normalize(prompt: str) -> str:
        if not prompt:
            return "autonomous execution"
        # Remove extra whitespace and trim
        return " ".join(prompt.strip().split())


class IntentExtractor:
    """Deduces core product category and business objectives from prompt text."""
    @staticmethod
    def extract(prompt_text: str) -> Dict[str, any]:
        text = prompt_text.lower()
        
        # Categorization logic
        category = "General Web Application"
        if "crm" in text:
            category = "CRM Platform"
        elif "saas" in text or "tenant" in text:
            category = "SaaS Multi-tenant Platform"
        elif "e-commerce" in text or "shop" in text or "cart" in text:
            category = "E-Commerce System"
        elif "blog" in text:
            category = "Content Management System"
        elif "cli" in text:
            category = "Command Line Tool"
            
        objectives = []
        if "login" in text or "auth" in text:
            objectives.append("Secure user identity authentication control")
        if "database" in text or "db" in text or "migrations" in text:
            objectives.append("Relational schema data model persistence")
        if "track" in text or "dashboard" in text:
            objectives.append("Performance metrics tracking visual dashboard")
            
        if not objectives:
            objectives.append(f"Deploy scalable {category} service infrastructure")

        return {
            "business_goal": f"Deliver a fully functional {category} meeting requirements.",
            "business_objectives": objectives,
            "category": category
        }


class EntityExtractor:
    """Identifies actors, modules, and integrations in user prompts."""
    @staticmethod
    def extract(prompt_text: str) -> Dict[str, List[str]]:
        text = prompt_text.lower()
        actors = ["System Administrator"]
        
        # Deduce actors/users
        if "student" in text:
            actors.append("Student User")
        if "teacher" in text:
            actors.append("Teacher Administrator")
        if "customer" in text or "client" in text:
            actors.append("Customer Client")
            
        modules = []
        if "auth" in text or "login" in text:
            modules.append("Authentication Module")
        if "database" in text or "db" in text:
            modules.append("Database Migrations Layer")
        if "api" in text or "route" in text:
            modules.append("REST Controller Layer")

        return {
            "primary_users": [actors[-1]],
            "secondary_users": [actors[0]],
            "modules": modules
        }


class RequirementClassifier:
    """Segregates functional requirement features from non-functional parameters."""
    @staticmethod
    def classify(prompt_text: str) -> Dict[str, List[Dict[str, str]]]:
        text = prompt_text.lower()
        functional = []
        non_functional = []
        
        # Populate basic classification lists
        if "login" in text or "auth" in text:
            functional.append({
                "id": "FR-AUTH",
                "name": "User Authentication",
                "description": "System must support secure user login and token validation.",
                "priority": "HIGH"
            })
            non_functional.append({
                "id": "NFR-SEC",
                "name": "Password Encryption",
                "type": "security",
                "description": "Encrypt user passwords using standard hashing algorithms.",
                "target": "Zero clear-text passwords stored"
            })
            
        if "database" in text or "db" in text:
            functional.append({
                "id": "FR-DB",
                "name": "Data Schema Migration",
                "description": "Apply and track schema version controls via database migrations.",
                "priority": "HIGH"
            })
            
        # Default fallback requirements
        if not functional:
            functional.append({
                "id": "FR-CORE",
                "name": "Core Application Controller",
                "description": "Execute main application functions specified in the goal.",
                "priority": "HIGH"
            })
            
        non_functional.append({
            "id": "NFR-PERF",
            "name": "Low Latency Scan Execution",
            "type": "performance",
            "description": "Scan and understand workspace specifications with minimal CPU delay.",
            "target": "Under 300ms latency"
        })

        return {
            "functional": functional,
            "non_functional": non_functional
        }


class EvidenceCollector:
    """Combines WDE scanning inventories with prompt expectations."""
    @staticmethod
    def merge(prompt_info: dict, wde_inventories: Dict[str, dict]) -> Dict[str, any]:
        metadata = wde_inventories.get("workspace.metadata", {})
        languages = wde_inventories.get("language.inventory", {}).get("languages", {})
        frameworks = wde_inventories.get("framework.inventory", {}).get("frameworks", {})
        
        # Evidence mapping
        files_scanned = []
        conventions = {
            "file_naming": "unknown",
            "styling": "unknown",
            "testing": "unknown"
        }
        
        # Read files scanned
        winv = wde_inventories.get("workspace.inventory", {})
        for f in winv.get("files", []):
            files_scanned.append(f["path"])
            
        # Parse conventions
        if "nextjs" in frameworks:
            conventions["file_naming"] = "kebab-case"
            conventions["styling"] = "tailwind"
            conventions["testing"] = "jest/vitest"
        elif "python" in languages:
            conventions["file_naming"] = "snake_case"
            conventions["styling"] = "none"
            conventions["testing"] = "unittest/pytest"

        return {
            "files_scanned": files_scanned[:10], # Cap at first 10 for log brevity
            "conventions_detected": conventions
        }


class RequirementExpander:
    """Uses engineering templates to expand sparse prompts into complete specification definitions."""
    @staticmethod
    def expand(prompt_text: str, category: str, base_reqs: dict) -> dict:
        text = prompt_text.lower()
        expanded_func = list(base_reqs.get("functional", []))
        expanded_nfunc = list(base_reqs.get("non_functional", []))
        
        # Expansion Rules Engine
        if category == "SaaS Multi-tenant Platform":
            expanded_func.append({
                "id": "FR-TENANT",
                "name": "Multi-tenant Isolation Controls",
                "description": "Ensure tenant data separation via database logic or RLS constraints.",
                "priority": "HIGH"
            })
            
        if "api" in text or "route" in text:
            expanded_func.append({
                "id": "FR-API",
                "name": "REST API Endpoints",
                "description": "Expose JSON router endpoints mapping model transactions.",
                "priority": "MEDIUM"
            })
            expanded_nfunc.append({
                "id": "NFR-API-RATE",
                "name": "API Rate Limiting",
                "type": "reliability",
                "description": "Limit API calls per IP to prevent service exhaustion.",
                "target": "100 requests per minute"
            })

        return {
            "functional": expanded_func,
            "non_functional": expanded_nfunc
        }


class ConfidenceCalculator:
    """Calculates factual certainty and completeness flags based on workspace files."""
    @staticmethod
    def calculate(wde_inventories: Dict[str, dict]) -> Dict[str, any]:
        frameworks = wde_inventories.get("framework.inventory", {}).get("frameworks", {})
        metadata = wde_inventories.get("workspace.metadata", {})
        
        factors = {
            "database_schema_confidence": 1.0 if "prisma" in frameworks or "sqlite" in frameworks else 0.0,
            "auth_confidence": 1.0 if "nextjs" in frameworks else 0.5,
            "docker_confidence": 1.0 if "docker" in frameworks else 0.0,
            "ci_cd_confidence": 1.0 if metadata.get("total_files", 0) > 20 else 0.0 # Mock factor
        }
        
        avg_score = sum(factors.values()) / len(factors)
        return {
            "aggregate_score": round(avg_score, 2),
            "factors": factors
        }


class ClarificationEngine:
    """Highlights high-risk ambiguities requiring user confirmation."""
    @staticmethod
    def inspect(confidence_score: float, prompt_text: str) -> List[str]:
        unknowns = []
        text = prompt_text.lower()
        
        if confidence_score < 0.70:
            unknowns.append("The target database schema structure could not be identified from active workspace indicators.")
            
        if "auth" in text and "jwt" not in text and "oauth" not in text:
            unknowns.append("Identify exact authentication standard (JWT vs OAuth session cookie tokens) required.")

        return unknowns


class UniversalRequirementUnderstandingEngine:
    """Coordinator Orchestrator running the SPEC-002 URUE pipeline."""
    def __init__(self, workspace_path: str, event_bus: EventBus = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.event_bus = event_bus if event_bus else EventBus(self.workspace_path)
        self.output_file = self.workspace_path / ".aetheris" / "execution" / "requirement.json"

    def understand(self, prompt: str, wde_inventories: Dict[str, dict]) -> Dict[str, any]:
        """Orchestrates prompt normalization, entity/intent parsing, evidence merge, and expands specifications."""
        self.event_bus.publish("RequirementIngestStarted", "URUE", {"prompt": prompt})
        
        # 1. Normalize prompt
        normalized_prompt = PromptNormalizer.normalize(prompt)
        
        # 2. Extract Business intent
        biz_info = IntentExtractor.extract(normalized_prompt)
        
        # 3. Extract entities
        entity_info = EntityExtractor.extract(normalized_prompt)
        
        # 4. Classify core base requirements
        base_reqs = RequirementClassifier.classify(normalized_prompt)
        
        # 5. Merge workspace evidence
        evidence_info = EvidenceCollector.merge(biz_info, wde_inventories)
        
        # 6. Expand requirements
        expanded_reqs = RequirementExpander.expand(normalized_prompt, biz_info["category"], base_reqs)
        
        # 7. Calculate confidence factors
        confidence_info = ConfidenceCalculator.calculate(wde_inventories)
        
        # 8. Check clarifications
        unknowns = ClarificationEngine.inspect(confidence_info["aggregate_score"], normalized_prompt)

        # 9. Format output model
        requirement_data = {
            "business": {
                "business_goal": biz_info["business_goal"],
                "business_objectives": biz_info["business_objectives"]
            },
            "users": {
                "primary_users": entity_info["primary_users"],
                "secondary_users": entity_info["secondary_users"],
                "personas": [
                    {
                        "name": entity_info["primary_users"][0],
                        "role": "Standard application operator role",
                        "goals": ["Access secure modules", "Transact model actions"]
                    }
                ]
            },
            "modules": [
                {
                    "name": m,
                    "description": f"Extracted service capability for {m}",
                    "category": "auth" if "auth" in m.lower() else "database" if "database" in m.lower() else "other"
                } for m in entity_info["modules"]
            ],
            "requirements": expanded_reqs,
            "dependencies": {
                "external_integrations": ["local_storage"],
                "module_dependencies": [
                    {
                        "source": "api_controllers",
                        "target": "database_migrations",
                        "relationship": "depends_on"
                    }
                ]
            },
            "constraints": {
                "technical_constraints": [f"Language mapping target: {list(wde_inventories.get('language.inventory', {}).get('languages', {}).keys())}"],
                "compliance_requirements": ["GDPR"],
                "deployment_targets": ["Docker"]
            },
            "confidence": confidence_info,
            "evidence": evidence_info,
            "unknowns": unknowns,
            "risks": [
                {
                    "severity": "HIGH" if confidence_info["aggregate_score"] < 0.60 else "MEDIUM",
                    "likelihood": "MEDIUM",
                    "description": "Missing database schema configurations may lead to un-migrated tables."
                }
            ],
            "assumptions": [
                "Assume SQLite is local storage database fallback if PostgreSQL is un-configured."
            ]
        }

        # 10. Schema verification & persistence
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(json.dumps(requirement_data, indent=2), encoding="utf-8")
        
        self.event_bus.publish("RequirementIngestCompleted", "URUE", {"confidence": confidence_info["aggregate_score"]})
        
        return requirement_data
