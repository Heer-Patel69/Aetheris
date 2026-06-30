import time
import os
import sys
import json
from pathlib import Path

# Add runtime directory to path
GLOBAL_AETHERIS_DIR = Path("~/.aetheris").expanduser()
sys.path.insert(0, str(GLOBAL_AETHERIS_DIR / "runtime"))

try:
    from kernel.goal_manager import GoalManager
except ImportError as e:
    sys.stderr.write(f"Error loading goal manager: {e}\n")
    sys.exit(1)

def run_benchmark():
    workspace = Path(r"c:\AI\Agency owner")
    goal_manager = GoalManager(workspace)
    
    print("Starting Intent & Product Understanding Engine Benchmark...")
    
    start_time = time.time()
    understanding = goal_manager.expand_goal("Build a basic student workspace tracker")
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    # Calculate parsing metrics
    num_personas = len(understanding.get("user_personas", []))
    num_rules = len(understanding.get("business_rules", []))
    num_features = len(understanding.get("feature_inventory", []))
    num_tables = len(understanding.get("database_entities", {}).get("sql_tables", []))
    num_models = len(understanding.get("database_entities", {}).get("prisma_models", []))
    
    print(f"Benchmark finished in {elapsed_ms}ms:")
    print(f"  - User Personas Discovered: {num_personas}")
    print(f"  - Business Rules Discovered: {num_rules}")
    print(f"  - Features Discovered: {num_features}")
    print(f"  - DB Schema Tables/Models Discovered: {num_tables + num_models}")
    
    # Record benchmark profile to benchmarks directory
    benchmark_dir = GLOBAL_AETHERIS_DIR / "benchmarks"
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    benchmark_file = benchmark_dir / "goal-manager-benchmarks.jsonl"
    
    profile = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine": "Intent & Product Understanding Engine (IPUE)",
        "elapsed_ms": elapsed_ms,
        "metrics": {
            "discovered_personas": num_personas,
            "discovered_rules": num_rules,
            "discovered_features": num_features,
            "discovered_db_entities": num_tables + num_models
        }
    }
    
    with open(benchmark_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(profile) + "\n")
        
    print(f"Benchmark profile written to {benchmark_file}")

if __name__ == "__main__":
    run_benchmark()
