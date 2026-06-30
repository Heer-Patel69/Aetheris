import sys
import json
from orchestration.config import ConfigManager
if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python config.py --workspace <path> --config <name> [--schema <name>]\n")
        sys.exit(1)
    workspace = None
    config_name = None
    schema = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--workspace" and i+1 < len(sys.argv):
            workspace = sys.argv[i+1]
        elif sys.argv[i] == "--config" and i+1 < len(sys.argv):
            config_name = sys.argv[i+1]
        elif sys.argv[i] == "--schema" and i+1 < len(sys.argv):
            schema = sys.argv[i+1]
    if not workspace or not config_name:
        sys.stderr.write("Error: --workspace and --config are required.\n")
        sys.exit(1)
    manager = ConfigManager(workspace)
    cfg = manager.load_config(config_name, schema)
    print(json.dumps(cfg, indent=2))
