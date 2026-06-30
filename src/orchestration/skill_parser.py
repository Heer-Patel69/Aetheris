import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("CRITICAL: 'pyyaml' is required by Skill Parser.\n")
    sys.exit(1)

class SkillParser:
    def __init__(self):
        pass

    def _extract_capabilities(self, content, frontmatter):
        """
        Dynamically extracts capabilities, languages, and frameworks from markdown body
        by searching for keyword markers if they are not defined in the frontmatter.
        """
        capabilities = set(frontmatter.get("capabilities", []))
        languages = set(frontmatter.get("languages", []))
        frameworks = set(frontmatter.get("frameworks", []))
        keywords = set(frontmatter.get("keywords", []))
        
        content_lower = content.lower()
        
        # Languages indicator checks
        language_map = {
            "typescript": ["typescript", "ts"],
            "javascript": ["javascript", "js", "node.js", "nodejs"],
            "python": ["python", "py"],
            "sql": ["sql", "postgres", "mysql", "sqlite"],
            "go": ["golang", "go mod", "go.mod"],
            "rust": ["rust", "cargo.toml"],
            "php": ["php", "composer.json"]
        }
        for lang, indicators in language_map.items():
            if any(ind in content_lower for ind in indicators):
                languages.add(lang)
                
        # Frameworks indicator checks
        framework_map = {
            "react": ["react", "jsx", "tsx"],
            "nextjs": ["next.js", "nextjs", "next config"],
            "vite": ["vite", "vite.config"],
            "supabase": ["supabase", "supabase/config"],
            "django": ["django", "manage.py"],
            "fastapi": ["fastapi", "uvicorn"],
            "tailwind": ["tailwindcss", "tailwind"]
        }
        for fw, indicators in framework_map.items():
            if any(ind in content_lower for ind in indicators):
                frameworks.add(fw)
                
        # Keywords extract from description and headers
        desc = frontmatter.get("description", "").lower()
        words = re.findall(r"\b[a-zA-Z]{4,15}\b", desc)
        for w in words:
            if w not in ("with", "this", "that", "from", "your", "under"):
                keywords.add(w)
                
        return list(capabilities), list(languages), list(frameworks), list(keywords)

    def parse_skill(self, file_path):
        """
        Reads and parses SKILL.md. Extracts YAML frontmatter and infers missing properties (ADR-001).
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            frontmatter = {}
            body = content
            
            # Check for standard YAML frontmatter blocks
            if content.startswith("---"):
                parts = content.split("---")
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        body = "---".join(parts[2:])
                    except yaml.YAMLError as e:
                        sys.stderr.write(f"YAML frontmatter parse error in {file_path}: {e}\n")
                        frontmatter = {}
                        
            if not isinstance(frontmatter, dict):
                frontmatter = {}

            # Infer missing fields with defaults
            folder_name = file_path.parent.name
            skill_id = frontmatter.get("id", folder_name)
            name = frontmatter.get("name", folder_name.replace("agency-", "").replace("-", " ").title())
            desc = frontmatter.get("description", "No description provided.")
            version = frontmatter.get("version", "2.1.0")
            
            # Determine Division from name or folder structure
            division = frontmatter.get("division", "specialized")
            if "marketing" in folder_name or "instagram" in folder_name or "twitter" in folder_name:
                division = "marketing"
            elif "developer" in folder_name or "architect" in folder_name or "engineer" in folder_name:
                division = "engineering"
            elif "security" in folder_name or "auditor" in folder_name:
                division = "security"
            elif "gis" in folder_name or "map" in folder_name or "geography" in folder_name:
                division = "gis"

            caps, langs, fws, keys = self._extract_capabilities(body, frontmatter)
            
            # Build structured Skill Object
            skill_object = {
                "id": skill_id,
                "name": name,
                "description": desc,
                "version": version,
                "division": division,
                "capabilities": caps,
                "languages": langs,
                "frameworks": fws,
                "keywords": keys,
                "permissions": frontmatter.get("permissions", ["read_workspace"]),
                "complexity": frontmatter.get("complexity", "moderate"),
                "execution_cost": frontmatter.get("execution_cost", 0.0),
                "estimated_context_tokens": frontmatter.get("estimated_context_tokens", 2000),
                "location": str(file_path.parent),
                "status": "healthy"
            }
            
            return skill_object
            
        except Exception as e:
            sys.stderr.write(f"SkillParser error on {file_path}: {e}\n")
            return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python skill_parser.py <path_to_SKILL.md>\n")
        sys.exit(1)
        
    parser = SkillParser()
    obj = parser.parse_skill(sys.argv[1])
    import json
    print(json.dumps(obj, indent=2))