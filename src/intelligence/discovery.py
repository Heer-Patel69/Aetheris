import os
import json

class ProjectDiscovery:
    """
    Performs initial and continuous repository scanning.
    Detects technologies, frameworks, build systems, CI/CD, etc.
    """
    def __init__(self, project_root):
        self.project_root = project_root
        self.state = {}

    def scan(self):
        """Scans the repository and infers architecture and state."""
        self.state = {
            "has_package_json": os.path.exists(os.path.join(self.project_root, "package.json")),
            "has_requirements_txt": os.path.exists(os.path.join(self.project_root, "requirements.txt")),
            "has_docker": os.path.exists(os.path.join(self.project_root, "Dockerfile")),
            "has_github_actions": os.path.exists(os.path.join(self.project_root, ".github", "workflows")),
            "is_python": False,
            "is_node": False,
        }
        
        if self.state["has_package_json"]:
            self.state["is_node"] = True
            
        if self.state["has_requirements_txt"] or os.path.exists(os.path.join(self.project_root, "pyproject.toml")):
            self.state["is_python"] = True

        print("[Discovery] Project structure analyzed.")
        return self.state

    def get_state(self):
        return self.state
