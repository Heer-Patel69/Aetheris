import sys
import json
from pathlib import Path
from kernel.utils import is_safe_path, initialize_perimeter

# Attempt to load pyyaml
try:
    import yaml
except ImportError:
    sys.stderr.write("CRITICAL: 'pyyaml' is required by Plugin Manager.\n")
    sys.exit(1)

class PluginManager:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        initialize_perimeter(self.workspace_path)
        
        self.global_plugin_registry = Path("~/.aetheris/plugins.yaml").expanduser()
        self.master_version = self._get_master_version()
        
    def _get_master_version(self):
        version_file = Path(__file__).parent.parent / "VERSION"
        if version_file.exists():
            with open(version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "2.1.0"

    def load_registry(self):
        """
        Loads the list of registered plugins from orchestration.plugins.yaml.
        """
        if not self.global_plugin_registry.exists():
            return {"plugins": []}
            
        if not is_safe_path(self.global_plugin_registry):
            raise PermissionError(f"Security Boundary Violation: Path {self.global_plugin_registry} is out of bounds.")
            
        try:
            with open(self.global_plugin_registry, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data else {"plugins": []}
        except Exception as e:
            sys.stderr.write(f"Plugin Registry Load Failure: {e}\n")
            return {"plugins": []}

    def _save_registry(self, registry):
        """
        Save registry changes to plugins.yaml.
        """
        if not is_safe_path(self.global_plugin_registry):
            raise PermissionError(f"Security Boundary Violation: Path {self.global_plugin_registry} is out of bounds.")
            
        self.global_plugin_registry.parent.mkdir(parents=True, exist_ok=True)
        with open(self.global_plugin_registry, "w", encoding="utf-8") as f:
            yaml.safe_dump(registry, f, default_flow_style=False)

    def validate_manifest(self, manifest_data):
        """
        Validates the structure and properties of a plugin manifest.
        """
        required_fields = ["name", "version", "path", "permissions", "hooks"]
        for field in required_fields:
            if field not in manifest_data:
                return False, f"Missing required manifest field: {field}"
                
        # Validate permissions
        allowed_permissions = {"read_workspace", "write_memory", "execute_scripts", "read_config"}
        for perm in manifest_data["permissions"]:
            if perm not in allowed_permissions:
                return False, f"Unauthorized plugin permission: {perm}"
                
        # Validate hook stages
        allowed_stages = {"INGEST", "DISCOVER", "PLAN", "ROUTE", "EXECUTE", "VERIFY", "COMMIT", "LOG"}
        for hook in manifest_data["hooks"]:
            if "stage" not in hook or "priority" not in hook:
                return False, "Hooks must specify 'stage' and 'priority'"
            if hook["stage"] not in allowed_stages:
                return False, f"Unauthorized hook stage: {hook['stage']}"
                
        return True, ""

    def register_plugin(self, plugin_dir_path):
        """
        Registers a new plugin by parsing its manifest.yaml.
        """
        plugin_dir = Path(plugin_dir_path).resolve()
        manifest_path = plugin_dir / "manifest.yaml"
        
        if not manifest_path.exists():
            return {"status": "error", "message": f"manifest.yaml not found in {plugin_dir}"}
            
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = yaml.safe_load(f)
                
            is_valid, error_msg = self.validate_manifest(manifest_data)
            if not is_valid:
                return {"status": "error", "message": f"Invalid manifest: {error_msg}"}
                
            # Verify version compatibility (Major version matching)
            plugin_version = manifest_data["version"]
            plugin_major = plugin_version.split(".")[0]
            master_major = self.master_version.split(".")[0]
            
            if plugin_major != master_major:
                return {
                    "status": "error",
                    "message": f"Plugin version incompatible. Plugin requires v{plugin_major}, Aetheris Kernel is v{master_major}"
                }
                
            # Load and update registry
            registry = self.load_registry()
            # Remove duplicate entry if exists
            registry["plugins"] = [p for p in registry["plugins"] if p["name"] != manifest_data["name"]]
            
            new_entry = {
                "name": manifest_data["name"],
                "version": manifest_data["version"],
                "enabled": True,
                "path": str(plugin_dir),
                "permissions": manifest_data["permissions"],
                "hooks": manifest_data["hooks"]
            }
            
            registry["plugins"].append(new_entry)
            self._save_registry(registry)
            
            return {"status": "success", "message": f"Plugin '{manifest_data['name']}' registered successfully."}
            
        except Exception as e:
            return {"status": "error", "message": f"Registration failed: {e}"}

if __name__ == "__main__":
    if len(sys.argv) < 5 or "--workspace" not in sys.argv or "--register" not in sys.argv:
        sys.stderr.write("Usage: python plugins.py --workspace <path> --register <plugin_dir>\n")
        sys.exit(1)
        
    workspace = None
    plugin_path = None
    
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--workspace" and i+1 < len(sys.argv):
            workspace = sys.argv[i+1]
        elif sys.argv[i] == "--register" and i+1 < len(sys.argv):
            plugin_path = sys.argv[i+1]
            
    manager = PluginManager(workspace)
    res = manager.register_plugin(plugin_path)
    print(json.dumps(res, indent=2))