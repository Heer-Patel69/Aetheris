import os
import sys
import shutil
from pathlib import Path

GLOBAL_AETHERIS_DIR = Path("~/.aetheris").expanduser().resolve()
GLOBAL_SKILLS_DIR = Path("~/.gemini/config/skills").expanduser().resolve()
AGENTS_RULES_FILE = Path("~/.gemini/config/AGENTS.md").expanduser().resolve()

SKILL_MODULES = [
    "aetheris-kernel",
    "aetheris-project-discovery",
    "aetheris-skill-orchestrator",
    "aetheris-verification-engine",
    "aetheris-context-engine",
    "aetheris-memory-engine",
    "aetheris-product-intelligence"
]

def uninstall():
    print("=======================================================")
    print("Aetheris Kernel — Uninstaller")
    print("=======================================================\n")
    
    # 1. Remove global runtime directory
    if GLOBAL_AETHERIS_DIR.exists():
        print(f"Removing global runtime directory: {GLOBAL_AETHERIS_DIR}...")
        try:
            shutil.rmtree(GLOBAL_AETHERIS_DIR)
            print("  ✅ Removed global runtime.")
        except Exception as e:
            sys.stderr.write(f"  ❌ Error removing global runtime: {e}\n")
            
    # 2. Remove global skills
    print("Removing global skills...")
    for skill in SKILL_MODULES:
        skill_path = GLOBAL_SKILLS_DIR / skill
        if skill_path.exists():
            try:
                shutil.rmtree(skill_path)
                print(f"  ✅ Removed skill: {skill}")
            except Exception as e:
                sys.stderr.write(f"  ❌ Error removing skill {skill}: {e}\n")
                
    # 3. Clean up AGENTS.md rules
    if AGENTS_RULES_FILE.exists():
        print("Cleaning up AGENTS.md rule entries...")
        try:
            with open(AGENTS_RULES_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Locate rules block and remove it
            rule_marker = "## Aetheris Kernel v2.1"
            if rule_marker in content:
                parts = content.split(rule_marker)
                # Keep everything before the marker, and drop the rule block
                # In a real environment, we'd use a regex or string parse
                cleaned = parts[0]
                with open(AGENTS_RULES_FILE, "w", encoding="utf-8") as f:
                    f.write(cleaned.strip() + "\n")
                print("  ✅ Removed rules from AGENTS.md.")
            else:
                print("  ℹ️ Info: No rules block found in AGENTS.md. Skipping.")
        except Exception as e:
            sys.stderr.write(f"  ❌ Error cleaning AGENTS.md: {e}\n")
            
    print("\n=======================================================")
    print("Uninstallation complete. Aetheris Kernel has been removed.")
    print("=======================================================")

if __name__ == "__main__":
    uninstall()