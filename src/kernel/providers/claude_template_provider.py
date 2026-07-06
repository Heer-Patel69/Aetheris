import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any
from kernel.providers.base import TemplateCapability

class ClaudeTemplateProvider(TemplateCapability):
    """
    Concrete capability provider mapping the 'templates' capability to Claude Templates.
    Imports templates and translates them into valid Aetheris Skills and RFCs.
    """

    def __init__(self, workspace_path: str):
        self.workspace_root = Path(workspace_path).resolve()
        
        ecc_root = self.workspace_root / "third party" / "ECC-main"
        if (ecc_root / "ECC-main").exists():
            self.ecc_source = ecc_root / "ECC-main"
        else:
            self.ecc_source = ecc_root

        self.skills_target_dir = self.workspace_root / "skills" / "third_party" / "claude_templates"
        self.rfcs_target_dir = self.workspace_root / "rfcs" / "third_party"
        self._status = "stopped"

    def initialize(self, config: Dict[str, Any]) -> None:
        self._status = "initialized"

    def start(self) -> bool:
        self._status = "running"
        return True

    def stop(self) -> bool:
        self._status = "stopped"
        return True

    def get_status(self) -> str:
        return self._status

    def sync_templates(self) -> Dict[str, Any]:
        """
        Synchronizes all third-party templates, translating them
        into native Aetheris operational files.
        """
        results = {
            "skills_copied": 0,
            "rfcs_copied": 0,
            "errors": []
        }

        if not self.ecc_source.exists():
            results["errors"].append(f"ECC source directory not found: {self.ecc_source}")
            return results

        # 1. Synchronize Capability Skills
        skills_src_dir = self.ecc_source / "skills"
        if skills_src_dir.exists():
            try:
                self.skills_target_dir.mkdir(parents=True, exist_ok=True)
                for entry in os.scandir(skills_src_dir):
                    if entry.is_dir():
                        skill_md_path = Path(entry.path) / "SKILL.md"
                        if skill_md_path.exists():
                            try:
                                self._convert_and_write_skill(skill_md_path, entry.name)
                                results["skills_copied"] += 1
                            except Exception as e:
                                results["errors"].append(f"Failed to convert skill '{entry.name}': {e}")
            except Exception as e:
                results["errors"].append(f"Failed to scan third-party skills: {e}")

        # 2. Synchronize Global Governance Rules (AGENTS.md, CLAUDE.md, RULES.md)
        global_rule_files = ["AGENTS.md", "CLAUDE.md", "RULES.md"]
        for rule_file in global_rule_files:
            rule_path = self.ecc_source / rule_file
            if rule_path.exists():
                try:
                    self.rfcs_target_dir.mkdir(parents=True, exist_ok=True)
                    target_path = self.rfcs_target_dir / rule_file
                    content = rule_path.read_text(encoding="utf-8", errors="ignore")
                    
                    # Wrap rules in a standard Aetheris RFC-compliant header
                    rfc_header = f"---\nname: {rule_file.replace('.md', '')}\ndescription: Third-party template rules for Aetheris Kernel.\ntype: governance\n---\n\n"
                    target_path.write_text(rfc_header + content, encoding="utf-8")
                    results["rfcs_copied"] += 1
                except Exception as e:
                    results["errors"].append(f"Failed to copy rule file '{rule_file}': {e}")

        return results

    def _convert_and_write_skill(self, src_path: Path, folder_name: str) -> None:
        content = src_path.read_text(encoding="utf-8", errors="ignore")
        frontmatter = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---")
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    body = "---".join(parts[2:])
                except Exception as e:
                    sys.stderr.write(f"YAML parse warning for {src_path}: {e}\n")

        name = frontmatter.get("name", folder_name.replace("-", " ").title())
        desc = frontmatter.get("description", "No description provided.")
        desc = " ".join(desc.split())

        aetheris_frontmatter = {
            "name": name,
            "description": desc,
            "color": frontmatter.get("color", "slate"),
            "emoji": frontmatter.get("emoji", "🤖"),
            "vibe": frontmatter.get("vibe", "The specialized capability agent.")
        }

        yaml_block = yaml.dump(aetheris_frontmatter, default_flow_style=False, sort_keys=False)
        formatted_content = f"---\n{yaml_block}---\n{body}"

        target_file = self.skills_target_dir / f"{folder_name}.md"
        target_file.write_text(formatted_content, encoding="utf-8")
