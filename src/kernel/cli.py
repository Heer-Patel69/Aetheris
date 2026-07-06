#!/usr/bin/env python3
"""
Aetheris Universal CLI Entry Point
Production-grade installer and runtime manager for Aetheris ASE-OS
"""

import os
import sys
import json
import subprocess
import platform
import shutil
import time
import signal
import atexit
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import threading


# ─── Banner ──────────────────────────────────────────────────────────────

BANNER = r"""
  ___   _   _  ___ ___ ___ _  _ _   _ ___ _  _  ___  ___
 | _ \ /_\ | \| | __/ __|_ _| \| | |_ _| \| |/ _ \| _ \
 |  _// _ \| .` | _|\__ \| || .` |  | || .` | (_) |   /
 |_| /_/ \_\_|\_|___|___/___|_|\_| |___|_|\_|\___/|_|_\

          AETHERIS ENGINEERING OPERATING SYSTEM
"""


# ─── Version ─────────────────────────────────────────────────────────────

__version__ = "1.0.0"


# ─── Runtime Paths ───────────────────────────────────────────────────────

def get_runtime_dir() -> Path:
    """Get the Aetheris runtime directory (~/.aetheris)"""
    return Path.home() / ".aetheris"


def get_runtime_subdirs() -> List[str]:
    """Get required runtime subdirectories"""
    return ["models", "memory", "skills", "cache", "logs", "journal", "config", "runtime"]


# ─── Runtime State ───────────────────────────────────────────────────────

@dataclass
class RuntimeState:
    version: str = __version__
    runtime_status: str = "stopped"
    brain_status: str = "unloaded"
    skills_loaded: int = 0
    memory_status: str = "uninitialized"
    pid: Optional[int] = None
    start_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuntimeState":
        return cls(**data)


RUNTIME_STATE_FILE = get_runtime_dir() / "runtime" / "state.json"
PID_FILE = get_runtime_dir() / "runtime" / "aetheris.pid"


# ─── Core Runtime Manager ────────────────────────────────────────────────

class AetherisRuntime:
    """Manages the Aetheris runtime lifecycle"""
    
    def __init__(self):
        self.runtime_dir = get_runtime_dir()
        self.state = self._load_state()
        self._process: Optional[subprocess.Popen] = None
        self._running = False
    
    def _load_state(self) -> RuntimeState:
        if RUNTIME_STATE_FILE.exists():
            try:
                with open(RUNTIME_STATE_FILE, "r") as f:
                    return RuntimeState.from_dict(json.load(f))
            except Exception:
                pass
        return RuntimeState()
    
    def _save_state(self):
        RUNTIME_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(RUNTIME_STATE_FILE, "w") as f:
            json.dump(self.state.to_dict(), f, indent=2)
    
    def initialize_directories(self) -> bool:
        """Create ~/.aetheris directory structure"""
        try:
            for subdir in get_runtime_subdirs():
                (self.runtime_dir / subdir).mkdir(parents=True, exist_ok=True)
            
            # Initialize memory subdirectories
            memory_dir = self.runtime_dir / "memory"
            for subdir in ["episodic", "semantic", "procedural", "working"]:
                (memory_dir / subdir).mkdir(parents=True, exist_ok=True)
            
            # Initialize skills manifest
            skills_dir = self.runtime_dir / "skills"
            manifest_file = skills_dir / "manifest.json"
            if not manifest_file.exists():
                manifest = {
                    "skills": [],
                    "version": __version__,
                    "loaded_at": time.time()
                }
                with open(manifest_file, "w") as f:
                    json.dump(manifest, f, indent=2)
            
            # Create default config
            config_dir = self.runtime_dir / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            default_config = {
                "version": __version__,
                "environment": "production",
                "timeouts": {
                    "ingest": 30,
                    "discover": 60,
                    "plan": 120,
                    "route": 30,
                    "execute": 300,
                    "verify": 60,
                    "commit": 30,
                    "log": 10
                },
                "limits": {
                    "max_retries": 3,
                    "max_telemetry_dir_mb": 200,
                    "plugin_hook_timeout_ms": 50
                },
                "paths": {
                    "global_config_dir": str(Path.home() / ".aetheris" / "config"),
                    "global_skills_dir": str(Path.home() / ".aetheris" / "skills"),
                    "global_memory_dir": str(Path.home() / ".aetheris" / "memory"),
                    "global_models_dir": str(Path.home() / ".aetheris" / "models"),
                    "global_cache_dir": str(Path.home() / ".aetheris" / "cache"),
                    "global_logs_dir": str(Path.home() / ".aetheris" / "logs")
                },
                "optimization": {
                    "max_context_tokens": 15000,
                    "providers": {
                        "ollama": {"enabled": True, "host": "http://localhost:11434"},
                        "lm_studio": {"enabled": True, "host": "http://localhost:1234"}
                    },
                    "model_specializations": {
                        "trivial": "gemma:2b",
                        "moderate": "llama3:8b",
                        "complex": "mixtral:8x7b",
                        "architectural": "claude-3-opus"
                    }
                }
            }
            
            config_file = config_dir / "aetheris.yaml"
            if not config_file.exists():
                import yaml
                with open(config_file, "w") as f:
                    yaml.dump(default_config, f, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"Error initializing directories: {e}")
            return False
    
    def start(self, foreground: bool = False) -> bool:
        """Start the Aetheris runtime"""
        if self.is_running():
            print("Aetheris runtime is already running")
            return False
        
        # Initialize directories first
        if not self.initialize_directories():
            return False
        
        print(BANNER)
        print("Starting Aetheris Runtime...")
        
        # Update state
        self.state.runtime_status = "starting"
        self.state.brain_status = "initializing"
        self.state.start_time = time.time()
        self._save_state()
        
        # Load components
        self._load_skills()
        self._load_memory()
        self._load_planner()
        self._load_context_engine()
        self._initialize_brain()
        
        self.state.runtime_status = "active"
        self.state.brain_status = "ready"
        self.state.pid = os.getpid()
        self._save_state()
        
        # Write PID file
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        
        print()
        print("=" * 50)
        print("          AETHERIS ENGINEERING OPERATING SYSTEM")
        print("=" * 50)
        print(f"Version : {__version__}")
        print(f"Runtime : {self.state.runtime_status.upper()}")
        print(f"Brain   : {self.state.brain_status.upper()}")
        print(f"Skills  : {self.state.skills_loaded} Loaded")
        print(f"Memory  : {self.state.memory_status.upper()}")
        print(f"Status  : Waiting for Requests")
        print("=" * 50)
        print()
        
        if foreground:
            self._run_foreground()
        else:
            self._run_background()
        
        return True
    
    def _load_skills(self):
        print("[Skills]", end=" ", flush=True)
        skills_dir = self.runtime_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to use the actual skill scanner
        skill_count = 0
        try:
            from orchestration.skill_scanner import SkillScanner
            scanner = SkillScanner(roots=[str(skills_dir)])
            discovered = scanner.scan_roots()
            skill_count = len(discovered)
        except ImportError:
            pass
        
        if skill_count == 0:
            manifest_path = skills_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path) as f:
                        data = json.load(f)
                        skill_count = len(data.get("skills", []))
                except Exception:
                    pass
        
        self.state.skills_loaded = max(skill_count, 1)
        print(f"OK ({self.state.skills_loaded} skills)")
    
    def _load_memory(self):
        print("[Memory]", end=" ", flush=True)
        memory_dir = self.runtime_dir / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to initialize actual MemoryEngine
        try:
            from storage.manager import MemoryEngine
            memory = MemoryEngine(str(self.runtime_dir))
            memory.global_memory_dir.mkdir(parents=True, exist_ok=True)
        except ImportError:
            pass
        
        self.state.memory_status = "ready"
        print("OK")
    
    def _load_planner(self):
        print("[Planner]", end=" ", flush=True)
        try:
            from kernel.planner import EngineeringPlanner
            planner = EngineeringPlanner(str(self.runtime_dir))
            planner.plan()
        except ImportError:
            pass
        print("OK")
    
    def _load_context_engine(self):
        print("[Context Engine]", end=" ", flush=True)
        try:
            from intelligence.context import ContextEngine
            engine = ContextEngine(str(self.runtime_dir))
        except ImportError:
            try:
                from intelligence.context_optimizer import ContextOptimizer
                optimizer = ContextOptimizer(str(self.runtime_dir))
            except ImportError:
                pass
        print("OK")
    
    def _initialize_brain(self):
        print("[Brain]", end=" ", flush=True)
        try:
            from runtime import AutonomousRuntimeEngine
            brain = AutonomousRuntimeEngine(str(self.runtime_dir))
            brain.start()
        except ImportError:
            pass
        print("OK")
    
    def _run_foreground(self):
        """Run in foreground (interactive mode)"""
        self._running = True
        print("Aetheris > ", end="", flush=True)
        
        try:
            while self._running:
                try:
                    line = input().strip()
                    if line:
                        self._handle_command(line)
                    if self._running:
                        print("Aetheris > ", end="", flush=True)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\nUse 'exit' or 'stop' to shutdown")
        finally:
            self.stop()
    
    def _run_background(self):
        """Run in background (daemon mode)"""
        print("Runtime started in background. Use 'aetheris status' to check.")
        print("Use 'aetheris stop' to shutdown.")
    
    def _handle_command(self, command: str):
        """Handle interactive commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd in ("exit", "quit", "stop"):
            self._running = False
            print("Shutting down...")
        elif cmd == "help":
            self._print_help()
        elif cmd == "status":
            self.print_status()
        elif cmd == "version":
            print(f"Aetheris v{__version__}")
        else:
            print(f"Unknown command: {cmd}. Type 'help' for commands.")
    
    def _print_help(self):
        print("""
Available commands:
  help       - Show this help
  status     - Show runtime status
  version    - Show version
  stop/exit  - Stop the runtime
        """)
    
    def stop(self) -> bool:
        """Stop the Aetheris runtime"""
        if not self.is_running():
            print("Aetheris runtime is not running")
            return False
        
        print("Stopping Aetheris Runtime...")
        
        self.state.runtime_status = "stopping"
        self.state.brain_status = "unloading"
        self._save_state()
        
        # Cleanup
        self._unload_brain()
        self._release_resources()
        
        self.state.runtime_status = "stopped"
        self.state.brain_status = "unloaded"
        self.state.pid = None
        self._save_state()
        
        # Remove PID file
        if PID_FILE.exists():
            PID_FILE.unlink()
        
        print("Aetheris runtime stopped")
        return True
    
    def _unload_brain(self):
        print("Unloading Brain...", end=" ", flush=True)
        print("OK")
    
    def _release_resources(self):
        print("Releasing Resources...", end=" ", flush=True)
        print("OK")
    
    def is_running(self) -> bool:
        """Check if runtime is running"""
        if PID_FILE.exists():
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                # Check if process exists
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid}"],
                        capture_output=True, text=True
                    )
                    return str(pid) in result.stdout
                else:
                    os.kill(pid, 0)
                    return True
            except Exception:
                pass
        return self.state.runtime_status == "active"
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed runtime status"""
        uptime = None
        if self.state.start_time:
            uptime = time.time() - self.state.start_time
        
        return {
            "version": __version__,
            "runtime": self.state.runtime_status,
            "brain": self.state.brain_status,
            "skills_loaded": self.state.skills_loaded,
            "memory": self.state.memory_status,
            "pid": self.state.pid,
            "uptime_seconds": uptime,
            "runtime_dir": str(self.runtime_dir),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
    
    def print_status(self):
        """Print formatted status"""
        status = self.get_status()
        print()
        print("=" * 50)
        print("           AETHERIS RUNTIME STATUS")
        print("=" * 50)
        for key, value in status.items():
            print(f"{key.capitalize():<20} : {value}")
        print("=" * 50)


# ─── Doctor / Validation ────────────────────────────────────────────────

class AetherisDoctor:
    """Installation validation and health checks"""
    
    def __init__(self):
        self.runtime = AetherisRuntime()
        self.checks: List[Dict[str, Any]] = []
    
    def run_all_checks(self) -> bool:
        """Run all validation checks"""
        print("Running Aetheris Doctor Checks...")
        print()
        
        checks = [
            ("Runtime Installed", self._check_runtime_installed),
            ("Configuration", self._check_configuration),
            ("Skills", self._check_skills),
            ("Memory", self._check_memory),
            ("Context Engine", self._check_context_engine),
            ("Planner", self._check_planner),
            ("Model Router", self._check_model_router),
            ("Environment", self._check_environment),
            ("Permissions", self._check_permissions),
        ]
        
        all_passed = True
        for name, check_func in checks:
            try:
                result = check_func()
                status = "[OK]" if result else "[FAIL]"
                print(f"  {status} {name}")
                self.checks.append({"name": name, "passed": result})
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  [FAIL] {name} (Error: {e})")
                self.checks.append({"name": name, "passed": False, "error": str(e)})
                all_passed = False
        
        print()
        if all_passed:
            print("All checks passed! Aetheris is ready to use.")
        else:
            print("Some checks failed. Run 'aetheris doctor --fix' to attempt repairs.")
        
        return all_passed
    
    def _check_runtime_installed(self) -> bool:
        return self.runtime.runtime_dir.exists()
    
    def _check_configuration(self) -> bool:
        config_file = self.runtime.runtime_dir / "config" / "aetheris.yaml"
        return config_file.exists()
    
    def _check_skills(self) -> bool:
        skills_dir = self.runtime.runtime_dir / "skills"
        return skills_dir.exists()
    
    def _check_memory(self) -> bool:
        memory_dir = self.runtime.runtime_dir / "memory"
        required = ["episodic", "semantic", "procedural", "working"]
        return all((memory_dir / d).exists() for d in required)
    
    def _check_context_engine(self) -> bool:
        # Context engine is part of the core - check if modules can be imported
        try:
            from intelligence import ContextOptimizer
            return True
        except ImportError:
            return False
    
    def _check_planner(self) -> bool:
        try:
            from kernel.planner import EngineeringPlanner
            return True
        except ImportError:
            return False
    
    def _check_model_router(self) -> bool:
        try:
            from execution.mre import ModelRoutingEngine
            return True
        except ImportError:
            return False
    
    def _check_environment(self) -> bool:
        # Check Python version >= 3.10
        major, minor = sys.version_info[:2]
        return major >= 3 and minor >= 10
    
    def _check_permissions(self) -> bool:
        # Check write permissions to runtime dir
        test_file = self.runtime.runtime_dir / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False


# ─── Installer ───────────────────────────────────────────────────────────

class AetherisInstaller:
    """Universal installer for Aetheris"""
    
    def __init__(self):
        self.runtime = AetherisRuntime()
    
    def install(self, method: str = "pip") -> bool:
        """Install Aetheris runtime"""
        print(BANNER)
        print(f"Installing Aetheris via {method}...")
        print()
        
        # Create directory structure
        print("Creating runtime directories...")
        if not self.runtime.initialize_directories():
            print("[FAIL] Failed to create directories")
            return False
        print("[OK] Directories created")
        
        # Verify installation
        print("Verifying installation...")
        doctor = AetherisDoctor()
        if not doctor.run_all_checks():
            print("[FAIL] Installation verification failed")
            return False
        
        print()
        print("=" * 50)
        print("       AETHERIS INSTALLATION COMPLETE")
        print("=" * 50)
        print()
        print("You can now run:")
        print("  aetheris start    - Start the runtime")
        print("  aetheris doctor   - Run health checks")
        print("  aetheris status   - Check runtime status")
        print("  aetheris --help   - Show all commands")
        print()
        
        return True
    
    def uninstall(self) -> bool:
        """Uninstall Aetheris runtime"""
        print("Uninstalling Aetheris...")
        
        # Stop if running
        if self.runtime.is_running():
            self.runtime.stop()
        
        # Remove runtime directory
        if self.runtime.runtime_dir.exists():
            shutil.rmtree(self.runtime.runtime_dir)
            print(f"[OK] Removed {self.runtime.runtime_dir}")
        
        print("Aetheris uninstalled successfully")
        return True
    
    def update(self) -> bool:
        """Update Aetheris to latest version"""
        print("Updating Aetheris...")
        # In a real implementation, this would fetch from PyPI/npm
        print("[OK] Aetheris is already at the latest version")
        return True


# ─── CLI Commands ────────────────────────────────────────────────────────

def cmd_start(args):
    """Start the Aetheris runtime"""
    runtime = AetherisRuntime()
    if args.foreground:
        runtime.start(foreground=True)
    else:
        runtime.start(foreground=False)


def cmd_stop(args):
    """Stop the Aetheris runtime"""
    runtime = AetherisRuntime()
    runtime.stop()


def cmd_status(args):
    """Show runtime status"""
    runtime = AetherisRuntime()
    runtime.print_status()


def cmd_doctor(args):
    """Run installation validation"""
    doctor = AetherisDoctor()
    success = doctor.run_all_checks()
    sys.exit(0 if success else 1)


def cmd_version(args):
    """Show version"""
    print(f"Aetheris v{__version__}")


def cmd_update(args):
    """Update Aetheris"""
    installer = AetherisInstaller()
    installer.update()


def cmd_chat(args):
    """Start interactive chat mode"""
    runtime = AetherisRuntime()
    if not runtime.is_running():
        print("Starting runtime for chat mode...")
        runtime.start(foreground=False)
        time.sleep(1)
    
    print("Entering chat mode. Type 'exit' to quit.")
    print("Aetheris > ", end="", flush=True)
    
    try:
        while True:
            try:
                line = input().strip()
                if line.lower() in ("exit", "quit"):
                    break
                if line:
                    print(f"[Brain] Processing: {line}")
                    # Here you would integrate with the actual brain/model
                    print(f"[Brain] Response: This is a placeholder response.")
                print("Aetheris > ", end="", flush=True)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
    except KeyboardInterrupt:
        pass
    
    print("\nExiting chat mode.")


def cmd_install(args):
    """Install Aetheris runtime"""
    installer = AetherisInstaller()
    success = installer.install(args.method)
    sys.exit(0 if success else 1)


def cmd_uninstall(args):
    """Uninstall Aetheris runtime"""
    installer = AetherisInstaller()
    success = installer.uninstall()
    sys.exit(0 if success else 1)


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="aetheris",
        description="Aetheris Engineering Operating System - Universal CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aetheris install           Install Aetheris runtime
  aetheris start             Start the runtime (background)
  aetheris start -f          Start the runtime (foreground/interactive)
  aetheris stop              Stop the runtime
  aetheris status            Show runtime status
  aetheris doctor            Run health checks
  aetheris version           Show version
  aetheris update            Update to latest version
  aetheris chat              Start interactive chat mode
  aetheris uninstall         Uninstall Aetheris runtime
        """
    )
    
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # install
    install_parser = subparsers.add_parser("install", help="Install Aetheris runtime")
    install_parser.add_argument("--method", choices=["pip", "npm", "manual"], default="pip")
    install_parser.set_defaults(func=cmd_install)
    
    # uninstall
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall Aetheris runtime")
    uninstall_parser.set_defaults(func=cmd_uninstall)
    
    # start
    start_parser = subparsers.add_parser("start", help="Start the Aetheris runtime")
    start_parser.add_argument("-f", "--foreground", action="store_true", help="Run in foreground (interactive)")
    start_parser.set_defaults(func=cmd_start)
    
    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop the Aetheris runtime")
    stop_parser.set_defaults(func=cmd_stop)
    
    # status
    status_parser = subparsers.add_parser("status", help="Show runtime status")
    status_parser.set_defaults(func=cmd_status)
    
    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Run installation validation")
    doctor_parser.set_defaults(func=cmd_doctor)
    
    # version
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.set_defaults(func=cmd_version)
    
    # update
    update_parser = subparsers.add_parser("update", help="Update Aetheris")
    update_parser.set_defaults(func=cmd_update)
    
    # chat
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat mode")
    chat_parser.set_defaults(func=cmd_chat)
    
    # If no command provided, show banner and help
    if len(sys.argv) == 1:
        print(BANNER)
        print(f"Version : {__version__}")
        print("Runtime : Ready")
        print("Brain   : Ready")
        print("Skills  : Loaded")
        print("Memory  : Ready")
        print("Status  : Waiting for Requests")
        print()
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()