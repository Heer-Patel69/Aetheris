import os
import sys
import shutil
from pathlib import Path

# Config paths
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

RULES_BLOCK = """
## Aetheris Kernel v2.1 — Global Rules

When handling any task that involves coding, refactoring, planning, or multi-step execution:
1. Verify if the `aetheris-kernel` skill is available.
2. If available, always follow the Kernel's pipeline loop (INGEST ➔ DISCOVER ➔ PLAN ➔ ROUTE ➔ EXECUTE ➔ VERIFY ➔ COMMIT ➔ LOG).
3. Do not bypass verification gates or execute unverified shell commands.
4. Keep context packages minimal.
"""

class TransactionalInstaller:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir).resolve()
        self.backup_dir = Path("~/.aetheris_backup").expanduser().resolve()
        self.temp_build_dir = self.source_dir / "build"
        
    def _preflight_check(self):
        """
        Verify Python version and folder write permissions.
        """
        print("Running preflight diagnostics...")
        if sys.version_info < (3, 8):
            sys.stderr.write("Error: Python version 3.8+ is required.\n")
            return False
            
        # Test permission to write in global paths
        try:
            GLOBAL_AETHERIS_DIR.mkdir(parents=True, exist_ok=True)
            test_file = GLOBAL_AETHERIS_DIR / ".install_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            sys.stderr.write(f"Permission Error: Cannot write to {GLOBAL_AETHERIS_DIR}: {e}\n")
            return False
            
        print("Preflight check passed.")
        return True

    def _backup(self):
        """
        Backup existing global runtime configurations before overwriting.
        """
        if GLOBAL_AETHERIS_DIR.exists():
            print(f"Creating backup of existing global runtime to {self.backup_dir}...")
            try:
                if self.backup_dir.exists():
                    shutil.rmtree(self.backup_dir)
                shutil.copytree(GLOBAL_AETHERIS_DIR, self.backup_dir)
                print("Backup complete.")
            except Exception as e:
                sys.stderr.write(f"Warning: Backup failed: {e}. Proceeding with caution.\n")

    def _rollback(self):
        """
        Rollback changes if installation fails (ADR-010).
        """
        print("CRITICAL: Installation failed. Initiating rollback...")
        
        # Remove partial skills
        for skill in SKILL_MODULES:
            skill_target = GLOBAL_SKILLS_DIR / skill
            if skill_target.exists():
                try:
                    shutil.rmtree(skill_target)
                except Exception:
                    pass
                    
        # Restore backup runtime folder
        if self.backup_dir.exists():
            try:
                if GLOBAL_AETHERIS_DIR.exists():
                    shutil.rmtree(GLOBAL_AETHERIS_DIR)
                shutil.copytree(self.backup_dir, GLOBAL_AETHERIS_DIR)
                print("Rollback complete. Restored original configuration.")
            except Exception as e:
                sys.stderr.write(f"Error: Rollback failed: {e}. Runtime may be in a corrupted state.\n")
        else:
            # Delete partial runtime
            if GLOBAL_AETHERIS_DIR.exists():
                try:
                    shutil.rmtree(GLOBAL_AETHERIS_DIR)
                except Exception:
                    pass
            print("Rollback finished. Partial files removed.")

    def _build_and_deploy_skills(self):
        """
        Builds skills from templates and copies them to the global skills path.
        Copies the corresponding python scripts directly into their scripts/ folder.
        """
        print("Compiling and deploying global skills...")
        GLOBAL_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        
        for skill in SKILL_MODULES:
            src_skill = self.source_dir / "skills" / skill
            target_skill = GLOBAL_SKILLS_DIR / skill
            
            if not src_skill.exists():
                raise FileNotFoundError(f"Source skill folder not found: {src_skill}")
                
            # Copy skill structure
            if target_skill.exists():
                shutil.rmtree(target_skill)
            shutil.copytree(src_skill, target_skill)
            
            # Create scripts subfolder inside the skill
            scripts_dir = target_skill / "scripts"
            if scripts_dir.exists():
                shutil.rmtree(scripts_dir)
            
            # Deploy execution scripts and packages directly to the skill scripts folder (ADR-007)
            src_src_dir = self.source_dir / "src"
            shutil.copytree(src_src_dir, scripts_dir)
                
        print("Skills deployed.")

    def _create_global_dirs(self):
        """
        Create global directories and copy default config templates.
        """
        print("Creating global runtime directories...")
        (GLOBAL_AETHERIS_DIR / "config").mkdir(parents=True, exist_ok=True)
        (GLOBAL_AETHERIS_DIR / "logs").mkdir(parents=True, exist_ok=True)
        (GLOBAL_AETHERIS_DIR / "plugins").mkdir(parents=True, exist_ok=True)
        
        # Copy core python scripts recursively to the global runtime path
        src_src_dir = self.source_dir / "src"
        target_runtime_dir = GLOBAL_AETHERIS_DIR / "runtime"
        if target_runtime_dir.exists():
            shutil.rmtree(target_runtime_dir)
        shutil.copytree(src_src_dir, target_runtime_dir)
            
        # Copy default configs ONLY if they don't exist (preserves user settings)
        src_config_dir = self.source_dir / "config"
        for config_file in src_config_dir.glob("*.yaml"):
            target_file = GLOBAL_AETHERIS_DIR / "config" / config_file.name
            if not target_file.exists():
                shutil.copy(config_file, target_file)
                
        # Copy schemas
        (GLOBAL_AETHERIS_DIR / "schemas").mkdir(parents=True, exist_ok=True)
        src_schema_dir = self.source_dir / "schemas"
        for schema_file in src_schema_dir.glob("*.json"):
            shutil.copy(schema_file, GLOBAL_AETHERIS_DIR / "schemas" / schema_file.name)
            
        print("Global directories and configurations initialized.")

    def _inject_agents_rules(self):
        """
        Appends global activation rules to AGENTS.md.
        """
        print("Injecting Kernel rules to AGENTS.md...")
        AGENTS_RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        current_rules = ""
        if AGENTS_RULES_FILE.exists():
            with open(AGENTS_RULES_FILE, "r", encoding="utf-8") as f:
                current_rules = f.read()
                
        # Inject rules only if they do not already exist
        if "Aetheris Kernel" not in current_rules:
            with open(AGENTS_RULES_FILE, "a", encoding="utf-8") as f:
                f.write(RULES_BLOCK)
            print("Rules injected.")
        else:
            print("Rules already present in AGENTS.md. Skipping injection.")

    def install(self):
        """
        Run the complete installation transaction.
        """
        if not self._preflight_check():
            sys.exit(1)
            
        try:
            self._backup()
            self._create_global_dirs()
            self._build_and_deploy_skills()
            self._inject_agents_rules()
            
            # Clean up backup on success
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
                
            print("\n=======================================================")
            print("Aetheris Kernel v2.1 installed successfully.")
            print("Restart Antigravity to activate the global runtime.")
            print("=======================================================")
            
        except Exception as e:
            sys.stderr.write(f"Installation Error: {e}\n")
            self._rollback()
            sys.exit(1)

if __name__ == "__main__":
    source_root = Path(__file__).parent.parent
    installer = TransactionalInstaller(source_root)
    
    action = "install"
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
    if action == "install" or action == "update":
        installer.install()
    elif action == "uninstall":
        print("To uninstall, remove '~/.aetheris' and skills in '~/.gemini/config/skills/' starting with 'aetheris-'.")
    else:
        sys.stderr.write(f"Unknown action: {action}\n")
        sys.exit(1)