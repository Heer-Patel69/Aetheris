import os
import sys
from pathlib import Path

# Attempt to load pyyaml
try:
    import yaml
except ImportError:
    sys.stderr.write("CRITICAL: 'pyyaml' is required by Build script.\n")
    sys.exit(1)

class SkillBuilder:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir).resolve()
        
    def validate_skill_markdown(self, skill_name):
        """
        Validate that the skill folder contains SKILL.md and has correct frontmatter.
        """
        skill_dir = self.source_dir / "skills" / skill_name
        skill_file = skill_dir / "SKILL.md"
        
        if not skill_file.exists():
            print(f"  ❌ Error: {skill_name}/SKILL.md does not exist.")
            return False
            
        try:
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Verify basic YAML frontmatter exists
            if not content.startswith("---"):
                print(f"  ❌ Error: {skill_name}/SKILL.md is missing frontmatter markers.")
                return False
                
            parts = content.split("---")
            if len(parts) < 3:
                print(f"  ❌ Error: {skill_name}/SKILL.md has malformed frontmatter.")
                return False
                
            # Validate YAML syntax of frontmatter
            frontmatter = yaml.safe_load(parts[1])
            if not isinstance(frontmatter, dict):
                print(f"  ❌ Error: Frontmatter in {skill_name} is not a valid YAML dictionary.")
                return False
                
            if "name" not in frontmatter or "description" not in frontmatter:
                print(f"  ❌ Error: Frontmatter in {skill_name} is missing 'name' or 'description'.")
                return False
                
            return True
        except Exception as e:
            print(f"  ❌ Error: Exception parsing {skill_name}/SKILL.md: {e}")
            return False

    def build_all(self):
        print("=======================================================")
        print("Aetheris Kernel — Compiler (Build)")
        print("=======================================================\n")
        
        skills_dir = self.source_dir / "skills"
        if not skills_dir.exists():
            sys.stderr.write("Error: Source skills directory not found.\n")
            return False
            
        skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
        print(f"Found {len(skills)} skills to validate.")
        
        success = True
        for skill in skills:
            print(f"Validating skill: {skill}...")
            if not self.validate_skill_markdown(skill):
                success = False
                
        print("\n=======================================================")
        if success:
            print("STATUS: SUCCESS (All skills are valid and ready for install).")
            print("=======================================================")
            return True
        else:
            print("STATUS: FAILED (One or more skills are invalid).")
            print("=======================================================")
            return False

if __name__ == "__main__":
    source_root = Path(__file__).parent.parent
    builder = SkillBuilder(source_root)
    res = builder.build_all()
    sys.exit(0 if res else 1)