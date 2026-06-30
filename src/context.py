import sys
import json
from intelligence.context import ContextEngine
if __name__ == "__main__":
    if len(sys.argv) < 5 or "--workspace" not in sys.argv or "--task" not in sys.argv:
        sys.stderr.write("Usage: python context.py --workspace <path> --task <description>\n")
        sys.exit(1)
    workspace = None
    task = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--workspace" and i+1 < len(sys.argv):
            workspace = sys.argv[i+1]
        elif sys.argv[i] == "--task" and i+1 < len(sys.argv):
            task = sys.argv[i+1]
    engine = ContextEngine(workspace)
    pkg = engine.build_context_package(task)
    print(json.dumps(pkg, indent=2))
