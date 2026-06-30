import sys
import json
from intelligence.scanner import ProjectScanner
if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "--workspace":
        sys.stderr.write("Usage: python scanner.py --workspace <path> --output json\n")
        sys.exit(1)
    ws_path = sys.argv[2]
    scanner = ProjectScanner(ws_path)
    result = scanner.scan()
    print(json.dumps(result, indent=2))
