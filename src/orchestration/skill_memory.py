import os
from pathlib import Path

class SkillMemory:
    """
    Manages Project Skill Memory in .aetheris/project/skills_used.md
    Tracks skill executions, source, purpose, duration, cost, and active project knowledge references.
    """
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.project_dir = self.workspace_path / ".aetheris" / "project"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.skills_used_file = self.project_dir / "skills_used.md"
        self._initialize_file()

    def _initialize_file(self):
        """Initializes the skills_used.md file with standard headers if it doesn't exist."""
        if not self.skills_used_file.exists():
            with open(self.skills_used_file, "w", encoding="utf-8") as f:
                f.write("# Project Skill & Knowledge Memory\n\n")
                f.write("This file is automatically updated by Aetheris to log engineering session execution history.\n\n")
                
                f.write("## Engineering Session Records\n\n")
                f.write("| Session ID | Skill Name | Source | Category | Purpose | Reason Selected | Prompt Trigger | Execution Order | Dependencies | Input | Output | Duration | Status | Tokens | Cost |\n")
                f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
                
                f.write("\n## Project Knowledge References\n\n")
                f.write("### Used RFCs\n\n")
                f.write("### Used SPECs\n\n")
                f.write("### Used Templates\n\n")
                f.write("### Used Headroom Modules\n\n")
                f.write("### Used Integrations\n\n")
                f.write("### Used Models\n\n")

    def log_skill_usage(self, session_id, skill_name, source, category, purpose, reason_selected, prompt_trigger, execution_order, dependencies, input_desc, output_desc, duration, status, tokens, cost):
        """Logs a skill execution into the markdown table."""
        row = f"| {session_id} | {skill_name} | {source} | {category} | {purpose} | {reason_selected} | {prompt_trigger} | {execution_order} | {', '.join(dependencies)} | {input_desc} | {output_desc} | {duration:.2f}s | {status} | {tokens} | ${cost:.6f} |\n"
        
        try:
            with open(self.skills_used_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Find insertion point under "## Engineering Session Records" table
            table_index = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("| --- | --- |"):
                    table_index = i + 1
                    break
            
            if table_index != -1:
                lines.insert(table_index, row)
                with open(self.skills_used_file, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            else:
                # Fallback to appending
                with open(self.skills_used_file, "a", encoding="utf-8") as f:
                    f.write(row)
        except Exception as e:
            print(f"[SkillMemory] Error logging skill usage: {e}")

    def log_knowledge_reference(self, ref_type, ref_name):
        """
        Logs references to Used RFCs, Used SPECs, Used Templates, 
        Used Headroom Modules, Used Integrations, or Used Models.
        Ensures duplicates are not added.
        """
        ref_sections = {
            "rfc": "### Used RFCs",
            "spec": "### Used SPECs",
            "template": "### Used Templates",
            "headroom": "### Used Headroom Modules",
            "integration": "### Used Integrations",
            "model": "### Used Models"
        }

        header = ref_sections.get(ref_type.lower())
        if not header:
            return

        try:
            with open(self.skills_used_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if reference already logged
            bullet = f"- {ref_name}"
            if bullet in content:
                return

            lines = content.splitlines()
            target_idx = -1
            for i, line in enumerate(lines):
                if line.strip() == header:
                    target_idx = i + 1
                    break

            if target_idx != -1:
                # Insert the reference bullet right after the header
                # Ensure spacing
                lines.insert(target_idx, bullet)
                lines.insert(target_idx + 1, "")
                
                # Reconstruct and save
                # Filter out consecutive empty lines
                cleaned_lines = []
                prev_empty = False
                for line in lines:
                    if line.strip() == "":
                        if not prev_empty:
                            cleaned_lines.append(line)
                            prev_empty = True
                    else:
                        cleaned_lines.append(line)
                        prev_empty = False
                        
                with open(self.skills_used_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(cleaned_lines) + "\n")
        except Exception as e:
            print(f"[SkillMemory] Error logging knowledge reference: {e}")
