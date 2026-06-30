import os
import re
import json
from pathlib import Path

class GoalManager:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        
    def _find_files_by_pattern(self, pattern):
        """
        Recursively scans the workspace (up to depth 3) for files matching pattern.
        """
        matches = []
        ignored_dirs = {".git", "node_modules", "venv", ".venv", ".aetheris", "dist", "build"}
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                # Prune ignored dirs in-place
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                
                # Enforce depth boundary
                rel_path = Path(root).relative_to(self.workspace_path)
                if len(rel_path.parts) >= 3:
                    dirs.clear()
                    continue
                    
                for f in files:
                    if re.search(pattern, f, re.IGNORECASE):
                        matches.append(Path(root) / f)
        except Exception:
            pass
        return matches

    def _parse_sql_schemas(self):
        """
        Parses actual SQL files to extract table definitions.
        """
        tables = []
        sql_files = self._find_files_by_pattern(r"\.sql$")
        for fpath in sql_files:
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                # Find all table declarations
                matches = re.findall(r"CREATE\s+TABLE\s+(\w+)", content, re.IGNORECASE)
                for table in matches:
                    tables.append({
                        "name": table,
                        "source": str(fpath.relative_to(self.workspace_path))
                    })
            except Exception:
                pass
        return tables

    def _parse_prisma_schemas(self):
        """
        Parses Prisma schema files to extract models.
        """
        models = []
        prisma_files = self._find_files_by_pattern(r"\.prisma$")
        for fpath in prisma_files:
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                matches = re.findall(r"model\s+(\w+)\s*\{", content)
                for m in matches:
                    models.append({
                        "name": m,
                        "source": str(fpath.relative_to(self.workspace_path))
                    })
            except Exception:
                pass
        return models

    def _parse_markdown_sections(self, md_files):
        """
        Extracts bulleted items from standard markdown sections (e.g. Features, Rules).
        """
        extracted = {
            "personas": [],
            "business_rules": [],
            "features": []
        }
        
        section_patterns = {
            "personas": [r"#+.*?persona", r"#+.*?user.*?journey", r"#+.*?target.*?user"],
            "business_rules": [r"#+.*?business.*?rule", r"#+.*?logic.*?constraint", r"#+.*?rule"],
            "features": [r"#+.*?feature", r"#+.*?functional.*?requirement"]
        }
        
        for fpath in md_files:
            try:
                lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
                current_section = None
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        current_section = None
                        # Match current header against patterns
                        for sec_name, patterns in section_patterns.items():
                            if any(re.search(pat, stripped, re.IGNORECASE) for pat in patterns):
                                current_section = sec_name
                                break
                    elif current_section and (stripped.startswith("-") or stripped.startswith("*") or re.match(r"^\d+\.", stripped)):
                        # Extract list item content
                        item_text = re.sub(r"^[-*\d\.\s]+", "", stripped)
                        if item_text:
                            extracted[current_section].append({
                                "text": item_text,
                                "source": f"{fpath.relative_to(self.workspace_path)}"
                            })
            except Exception:
                pass
        return extracted

    def expand_goal(self, user_goal):
        """
        Aggregates natural language inputs and searches the workspace for real documentation,
        database schemas, and code to compile a non-simulated project understanding.
        """
        # Find all markdown files (PRDs, readmes, specs)
        md_files = self._find_files_by_pattern(r"\.md$|\.txt$")
        
        # Parse markdown files
        md_sections = self._parse_markdown_sections(md_files)
        
        # Parse database schemas
        sql_tables = self._parse_sql_schemas()
        prisma_models = self._parse_prisma_schemas()
        
        # Analyze project files to collect structural evidence
        evidence = []
        
        # Check for Docker configs
        dockerfiles = self._find_files_by_pattern(r"Dockerfile|docker-compose")
        if dockerfiles:
            evidence.append(f"Docker configuration detected in: {[str(d.relative_to(self.workspace_path)) for d in dockerfiles]}")
            
        # Check for Github Actions or CI files
        ci_files = self._find_files_by_pattern(r"\.github/workflows")
        if ci_files:
            evidence.append("GitHub Actions workflows detected.")
            
        # Check database setup files
        db_indicators = []
        if sql_tables:
            db_indicators.append(f"SQL tables: {[t['name'] for t in sql_tables]}")
            evidence.extend([f"SQL schema file found: {t['source']}" for t in sql_tables])
        if prisma_models:
            db_indicators.append(f"Prisma models: {[m['name'] for m in prisma_models]}")
            evidence.extend([f"Prisma schema file found: {m['source']}" for m in prisma_models])
        if db_indicators:
            evidence.append(f"Database schema entities found: {db_indicators}")
            
        # Compute confidence values based on evidence density
        confidence_metrics = {
            "database": 1.0 if (sql_tables or prisma_models) else (0.5 if "db" in user_goal.lower() or "database" in user_goal.lower() else 0.0),
            "docker": 1.0 if dockerfiles else 0.0,
            "ci_cd": 1.0 if ci_files else 0.0,
            "auth": 1.0 if any("auth" in f["text"].lower() for f in md_sections["features"]) else (0.5 if "auth" in user_goal.lower() else 0.0)
        }
        
        # Identify missing requirements
        missing_requirements = []
        if confidence_metrics["database"] == 0.0:
            missing_requirements.append("Database schema specification is missing or could not be detected.")
        if confidence_metrics["docker"] == 0.0:
            missing_requirements.append("Docker containers configuration (Dockerfile) is missing.")
        if confidence_metrics["ci_cd"] == 0.0:
            missing_requirements.append("CI/CD pipeline workflows are missing.")
            
        # Compile inferred subsystems based on confidence metrics
        inferred_subsystems = []
        if confidence_metrics["database"] > 0:
            inferred_subsystems.append("database_migrations")
        if confidence_metrics["auth"] > 0:
            inferred_subsystems.append("authentication")
        inferred_subsystems.extend(["api_controllers", "frontend_views", "unit_testing"])
        if confidence_metrics["docker"] > 0:
            inferred_subsystems.append("dockerization")
        if confidence_metrics["ci_cd"] > 0:
            inferred_subsystems.append("deployment_pipelines")

        # Build the final non-simulated understanding map
        understanding = {
            "product_vision": user_goal,
            "inferred_subsystems": inferred_subsystems,
            "user_personas": md_sections["personas"],
            "business_rules": md_sections["business_rules"],
            "feature_inventory": md_sections["features"],
            "database_entities": {
                "sql_tables": sql_tables,
                "prisma_models": prisma_models
            },
            "evidence": evidence,
            "confidence_scores": confidence_metrics,
            "missing_requirements": missing_requirements,
            "assumptions": [
                "Local workspace directory structure defines project boundaries.",
                "Workspace indicators reflect active stack choices."
            ]
        }
        
        # Save to project memory under .aetheris/
        try:
            out_path = self.workspace_path / ".aetheris" / "product.understanding.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(understanding, indent=2), encoding="utf-8")
        except Exception:
            pass
            
        return understanding
