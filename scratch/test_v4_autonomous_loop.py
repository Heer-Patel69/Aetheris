import os
import sys
from pathlib import Path

# Add runtime directory to path
GLOBAL_AETHERIS_DIR = Path("~/.aetheris").expanduser()
sys.path.insert(0, str(GLOBAL_AETHERIS_DIR / "runtime"))

try:
    from kernel.core import AetherisKernel
    from intelligence.decision import DecisionIntelligenceEngine
except ImportError as e:
    sys.stderr.write(f"Error loading core Aetheris packages: {e}\n")
    sys.exit(1)

def run_integration_test():
    print("=======================================================")
    print("Aetheris Kernel v4.0 — Autonomous Execution Test")
    print("=======================================================")
    
    # Initialize workspace paths
    workspace = Path(r"c:\AI\Agency owner")
    kernel = AetherisKernel(workspace)
    
    # Trigger Autonomous Engineering Execution
    goal = "Build a student workspace tracker with auth and payment checkout"
    success = kernel.run_autonomous_loop(goal)
    
    if success:
        # Verify tech-decisions.jsonl was logged
        die = DecisionIntelligenceEngine(workspace)
        records = die.get_decisions()
        print("\nVerifying stored Decision Intelligence Records:")
        for r in records:
            print(f"  - Topic: {r.get('topic')} | Choice: {r.get('choice')} | Confidence: {r.get('confidence') * 100}%")
            
        print("\n=======================================================")
        print("TEST SUCCESS: Autonomous execution pipeline verified.")
        print("=======================================================")
    else:
        print("TEST FAILED: Autonomous loop returned failure.")
        sys.exit(1)

if __name__ == "__main__":
    run_integration_test()
