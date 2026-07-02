import os
import sys
import time
import subprocess
from pathlib import Path

# Paths Setup
WORKSPACE_DIR = Path(__file__).parent.parent.parent.resolve()
AETHERIS_DIR = WORKSPACE_DIR / "aetheris"
WEB_DIR = AETHERIS_DIR / "web"
COMPILE_SCRIPT = AETHERIS_DIR / "scripts" / "compile_repo.py"

def get_watched_files():
    """Collect all files we want to monitor for changes."""
    files = {}
    
    # 1. Watch divisions.json
    div_json = WORKSPACE_DIR / "divisions.json"
    if div_json.exists():
        files[div_json] = div_json.stat().st_mtime
        
    # 2. Watch all md files in active divisions
    # Read divisions.json to get division folders
    divisions = []
    if div_json.exists():
        try:
            import json
            with open(div_json, "r", encoding="utf-8") as f:
                divisions = list(json.load(f).get("divisions", {}).keys())
        except Exception:
            pass
            
    for div in divisions:
        div_path = WORKSPACE_DIR / div
        if div_path.exists():
            for f in div_path.glob("*.md"):
                files[f] = f.stat().st_mtime
                
    # 3. Watch aetheris/rfcs
    rfcs_dir = AETHERIS_DIR / "rfcs"
    if rfcs_dir.exists():
        for f in rfcs_dir.glob("*.md"):
            files[f] = f.stat().st_mtime
            
    # 4. Watch aetheris/docs and aetheris/adrs
    docs_dir = AETHERIS_DIR / "docs"
    if docs_dir.exists():
        for f in docs_dir.glob("*.md"):
            files[f] = f.stat().st_mtime
            
    adrs_dir = AETHERIS_DIR / "adrs"
    if adrs_dir.exists():
        for f in adrs_dir.glob("*.md"):
            files[f] = f.stat().st_mtime
            
    return files

def run_compiler():
    """Run the repository compiler script."""
    print("\n[Watcher] Rebuilding repository database...")
    try:
        subprocess.run([sys.executable, str(COMPILE_SCRIPT)], check=True)
        print("[Watcher] Rebuild successful.\n")
    except subprocess.CalledProcessError as e:
        print(f"[Watcher] Rebuild failed: {e}\n")

def main():
    print("=======================================================")
    print("Aetheris Kernel — Hot Reload Dev Server")
    print("=======================================================")
    
    # Run initial compilation
    run_compiler()
    
    # Start Vite dev server as a subprocess
    print("Starting Vite development server...")
    try:
        vite_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(WEB_DIR),
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True
        )
    except Exception as e:
        print(f"Failed to start Vite: {e}")
        sys.exit(1)
        
    print("Watcher active. Monitoring repository files for changes...")
    
    # Simple file polling watcher loop
    last_files = get_watched_files()
    try:
        while True:
            time.sleep(2)
            current_files = get_watched_files()
            
            # Check for changes, additions, or deletions
            changed = False
            if set(current_files.keys()) != set(last_files.keys()):
                changed = True
            else:
                for path, mtime in current_files.items():
                    if last_files.get(path) != mtime:
                        changed = True
                        break
                        
            if changed:
                run_compiler()
                last_files = current_files
                
    except KeyboardInterrupt:
        print("\nStopping development server...")
        vite_proc.terminate()
        vite_proc.wait()
        print("Dev server stopped.")

if __name__ == "__main__":
    main()
