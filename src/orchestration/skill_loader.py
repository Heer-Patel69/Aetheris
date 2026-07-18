import os
from pathlib import Path

class SkillLoader:
    """
    Intelligent dynamic skill loader.
    Loads full skill content only after capability resolution is complete,
    ensuring token optimization and minimal runtime memory.
    """
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()

    def load_skill_content(self, skill_metadata):
        """Loads and returns the full content (body/instructions) of a resolved skill."""
        entry_point = skill_metadata.get("entry_point")
        if not entry_point or not os.path.exists(entry_point):
            return ""

        try:
            with open(entry_point, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Separate YAML frontmatter if it exists
            if content.startswith("---"):
                parts = content.split("---")
                if len(parts) >= 3:
                    # Return body only
                    return "---".join(parts[2:]).strip()
            
            return content.strip()
        except Exception as e:
            print(f"[SkillLoader] Error loading skill content from {entry_point}: {e}")
            return ""
