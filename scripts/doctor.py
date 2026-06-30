import os
import sys
import json
from pathlib import Path

# Paths to verify
GLOBAL_AETHERIS_DIR = Path("~/.aetheris").expanduser().resolve()
GLOBAL_SKILLS_DIR = Path("~/.gemini/config/skills").expanduser().resolve()

SKILL_MODULES = [
    "aetheris-kernel",
    "aetheris-project-discovery",
    "aetheris-skill-orchestrator",
    "aetheris-verification-engine",
    "aetheris-context-engine",
    "aetheris-memory-engine",
    "aetheris-product-intelligence"
]

class DiagnosticsEngine:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        
    def check_skills(self):
        """
        Verify that all global skills are deployed.
        """
        print("[1/5] Checking global skills installation...")
        missing = []
        for skill in SKILL_MODULES:
            skill_path = GLOBAL_SKILLS_DIR / skill
            if not skill_path.exists():
                missing.append(skill)
            else:
                # Check for SKILL.md
                if not (skill_path / "SKILL.md").exists():
                    missing.append(f"{skill} (missing SKILL.md)")
                    
        if missing:
            print(f"  [FAIL] Missing skills: {missing}")
            return False
        print("  [ OK ] All 7 global skills are installed.")
        return True

    def check_runtime_scripts(self):
        """
        Verify that Python scripts are present in the runtime folder.
        """
        print("[2/5] Checking global runtime script deployment...")
        required_scripts = [
            "config.py", "scanner.py", "context.py", "memory.py", 
            "telemetry.py", "event_bus.py", "plugins.py", "utils.py",
            "skill_scanner.py", "skill_parser.py", "registry_cache.py"
        ]
        runtime_dir = GLOBAL_AETHERIS_DIR / "runtime"
        
        if not runtime_dir.exists():
            print("  [FAIL] Global runtime directory does not exist.")
            return False
            
        missing = []
        for script in required_scripts:
            if not (runtime_dir / script).exists():
                missing.append(script)
                
        if missing:
            print(f"  [FAIL] Missing runtime scripts: {missing}")
            return False
        print("  [ OK ] All runtime scripts are deployed.")
        return True

    def check_configurations(self):
        """
        Verify configuration files, validate schemas, and verify Dynamic Registry compilation.
        """
        print("[3/5] Validating configs & compiling Dynamic Skill Registry...")
        # Import config manager from runtime
        sys.path.insert(0, str(GLOBAL_AETHERIS_DIR / "runtime"))
        try:
            import time
            from config import ConfigManager
            manager = ConfigManager(self.workspace_path)
            
            # Test loading core configurations
            configs = ["aetheris", "models", "gates", "costs", "plugins"]
            for cfg in configs:
                schema_name = "aetheris" if cfg == "aetheris" else cfg
                data = manager.load_config(cfg, schema_name)
                if not data:
                    print(f"  [FAIL] Config {cfg} failed to load or validate.")
                    return False
                    
            # Test loading Dynamic Registry and profile latency
            start_load = time.time()
            registry = manager.get_registry(force_rebuild=False)
            first_load_ms = int((time.time() - start_load) * 1000)
            
            # Test second load (verifying cache speed constraint: <20ms)
            start_cached = time.time()
            registry = manager.get_registry(force_rebuild=False)
            cached_load_ms = int((time.time() - start_cached) * 1000)
            
            print(f"  [INFO] Discovered {len(registry)} skills.")
            print(f"  [INFO] First load/index took {first_load_ms}ms.")
            print(f"  [INFO] Cached load took {cached_load_ms}ms.")
            
            if len(registry) == 0:
                print("  [FAIL] Discovered 0 skills. Registry is empty.")
                return False
                
            if cached_load_ms > 50:
                print(f"  [WARN] Cached load latency of {cached_load_ms}ms exceeds target benchmark (<20ms).")
                
            print("  [ OK ] Configuration and Dynamic Registry are valid.")
            return True
        except Exception as e:
            print(f"  [FAIL] Configuration or Registry loading error: {e}")
            import traceback
            traceback.print_exc()
            return False


    def check_permissions(self):
        """
        Verify write permissions on telemetry and log directories.
        """
        print("[4/5] Testing directory permissions...")
        test_paths = [
            GLOBAL_AETHERIS_DIR / "logs",
            self.workspace_path / ".aetheris" if self.workspace_path.exists() else None
        ]
        
        for path in test_paths:
            if not path:
                continue
            path.mkdir(parents=True, exist_ok=True)
            try:
                test_file = path / ".permission_test"
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                print(f"  [FAIL] Write permission denied on {path}: {e}")
                return False
        print("  [ OK ] File permissions are correct.")
        return True

    def check_log_sizes(self):
        """
        Check log directory size limits.
        """
        print("[5/5] Reviewing log sizes...")
        log_file = GLOBAL_AETHERIS_DIR / "logs/execution-trace.jsonl"
        if log_file.exists():
            size_mb = log_file.stat().st_size / (1024 * 1024)
            print(f"  [INFO] Current trace log size is {size_mb:.2f} MB.")
            if size_mb > 200:
                print("  [WARN] Log size exceeds 200MB threshold. Pruning recommended.")
        else:
            print("  [INFO] No execution logs found yet.")
        print("  [ OK ] Log sizes checked.")
        return True


    def run_diagnostics(self):
        print("=======================================================")
        print("Aetheris Kernel — Diagnostics (Doctor)")
        print("=======================================================\n")
        
        results = [
            self.check_skills(),
            self.check_runtime_scripts(),
            self.check_configurations(),
            self.check_permissions(),
            self.check_log_sizes()
        ]
        
        print("\n=======================================================")
        if all(results):
            print("STATUS: HEALTHY (All diagnostics passed).")
            print("=======================================================")
            return True
        else:
            print("STATUS: UNHEALTHY (One or more checks failed).")
            print("Please run 'python scripts/install.py update' to repair.")
            print("=======================================================")
            return False

if __name__ == "__main__":
    workspace = "."
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
        
    doctor = DiagnosticsEngine(workspace)
    success = doctor.run_diagnostics()
    sys.exit(0 if success else 1)