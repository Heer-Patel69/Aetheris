import os
import json
import sys
from pathlib import Path
from kernel.utils import is_safe_path, redact_secrets, initialize_perimeter

# Attempt to load pyyaml, fallback to simple parser or exit if not found
try:
    import yaml
except ImportError:
    # Diagnostic error to stderr for installation checks
    sys.stderr.write("CRITICAL: 'pyyaml' package is required but not installed.\n")
    sys.exit(1)

# Attempt to load jsonschema for validation, fallback to manual validation if not installed
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    sys.stderr.write("WARNING: 'jsonschema' package not installed. Falling back to basic structural checks.\n")
    HAS_JSONSCHEMA = False

class ConfigManager:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        initialize_perimeter(self.workspace_path)
        
        self.default_config_dir = Path(__file__).parent.parent / "config"
        self.global_config_dir = Path("~/.aetheris/config").expanduser()
        self.project_config_dir = self.workspace_path / ".aetheris/config"
        self.schema_dir = Path(__file__).parent.parent / "schemas"
        
        self._cache = {}

    def _deep_merge(self, dict_a, dict_b):
        """
        Deep merge two dictionaries. Values in dict_b override values in dict_a.
        """
        result = dict_a.copy()
        for key, val in dict_b.items():
            if key in result and isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = self._deep_merge(result[key], val)
            else:
                result[key] = val
        return result

    def _load_yaml(self, file_path):
        """
        Load and parse YAML configuration files safely.
        """
        if not file_path.exists():
            return {}
            
        if not is_safe_path(file_path):
            raise PermissionError(f"Security Violation: Access denied to config path {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Redact secrets before parsing
            cleaned_content = redact_secrets(content)
            try:
                data = yaml.safe_load(cleaned_content)
                return data if data else {}
            except yaml.YAMLError as e:
                sys.stderr.write(f"YAML Parse Error in {file_path}: {e}\n")
                return {}

    def _load_schema(self, schema_name):
        """
        Load JSON schema file.
        """
        schema_path = self.schema_dir / f"{schema_name}.schema.json"
        if not schema_path.exists():
            return None
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate_config(self, config_data, schema_name):
        """
        Validate configuration data against the schema.
        """
        schema = self._load_schema(schema_name)
        if not schema:
            return True, []
            
        if HAS_JSONSCHEMA:
            try:
                jsonschema.validate(instance=config_data, schema=schema)
                return True, []
            except jsonschema.ValidationError as e:
                return False, [str(e)]
        else:
            # Fallback basic structural checks if jsonschema is missing
            errors = []
            if "version" in schema and "version" not in config_data:
                errors.append("Missing required key: version")
            return len(errors) == 0, errors

    def get_registry(self, force_rebuild=False):
        """
        Dynamically loads the global skill registry. Merges static specialists.yaml
        as overrides if present, printing a deprecation warning (v3.0).
        """
        from orchestration.registry_cache import RegistryCache
        cache = RegistryCache(self.workspace_path)
        registry = cache.load_registry(force_rebuild)
        
        # Load legacy specialists.yaml overrides if present
        project_specialists = self.project_config_dir / "specialists.yaml"
        global_specialists = self.global_config_dir / "specialists.yaml"
        
        static_overrides = {}
        if project_specialists.exists():
            sys.stderr.write("DEPRECATION WARNING: Static project-level 'specialists.yaml' is deprecated in v3.0. Use dynamic discovery.\n")
            static_overrides = self._load_yaml(project_specialists)
        elif global_specialists.exists():
            sys.stderr.write("DEPRECATION WARNING: Static global 'specialists.yaml' is deprecated in v3.0. Use dynamic discovery.\n")
            static_overrides = self._load_yaml(global_specialists)
            
        if static_overrides:
            # Merge static overrides into the dynamic registry
            for key, val in static_overrides.items():
                if key in registry:
                    registry[key] = self._deep_merge(registry[key], val)
                else:
                    registry[key] = val
                    
        return registry

    def load_config(self, config_name, schema_name=None, runtime_overrides=None):
        """
        Load configuration across the hierarchy (Defaults -> Global -> Project -> Runtime)
        """
        # Deprecation warnings for specialists file queries
        if config_name == "specialists":
            sys.stderr.write("DEPRECATION WARNING: Querying specialists.yaml config is deprecated. Query registry instead.\n")

        cache_key = f"{config_name}_{json.dumps(runtime_overrides, sort_keys=True) if runtime_overrides else ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Shipped Defaults
        default_path = self.default_config_dir / f"{config_name}.yaml"
        config = self._load_yaml(default_path)

        # 2. User Global Overrides
        global_path = self.global_config_dir / f"{config_name}.yaml"
        if global_path.exists():
            global_config = self._load_yaml(global_path)
            config = self._deep_merge(config, global_config)

        # 3. Project Local Overrides
        project_path = self.project_config_dir / f"{config_name}.yaml"
        if project_path.exists():
            project_config = self._load_yaml(project_path)
            config = self._deep_merge(config, project_config)

        # 4. Runtime Overrides
        if runtime_overrides:
            config = self._deep_merge(config, runtime_overrides)

        # Validate
        if schema_name:
            is_valid, errors = self.validate_config(config, schema_name)
            if not is_valid:
                sys.stderr.write(f"Validation failed for config '{config_name}': {errors}\n")
                # Fallback: reload defaults
                config = self._load_yaml(default_path)

        self._cache[cache_key] = config
        return config


if __name__ == "__main__":
    # CLI entry point for diagnostics / testing
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