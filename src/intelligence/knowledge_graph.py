import os
import ast

class KnowledgeGraph:
    """
    Builds an internal knowledge graph of the codebase (classes, functions, etc).
    """
    def __init__(self, project_root, aetheris_dir):
        self.project_root = project_root
        self.aetheris_dir = aetheris_dir
        self.graph = {
            "classes": [],
            "functions": [],
            "imports": []
        }

    def update(self):
        """Scans the repository and updates the knowledge graph."""
        self.graph = {"classes": [], "functions": [], "imports": []}
        
        for root, dirs, files in os.walk(self.project_root):
            if ".aetheris" in root or ".git" in root or "node_modules" in root or "venv" in root:
                continue
                
            for file in files:
                if file.endswith(".py"):
                    self._parse_python(os.path.join(root, file))
                    
        self._save()

    def _parse_python(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=filepath)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.graph["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    self.graph["functions"].append(node.name)
                elif isinstance(node, ast.Import):
                    for n in node.names:
                        self.graph["imports"].append(n.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.graph["imports"].append(node.module)
        except Exception as e:
            # Skip unparseable files
            pass

    def _save(self):
        # Save to SQLite or JSON. We use a simple JSON file for this prototype.
        knowledge_dir = os.path.join(self.aetheris_dir, "knowledge")
        os.makedirs(knowledge_dir, exist_ok=True)
        import json
        with open(os.path.join(knowledge_dir, "graph.json"), "w", encoding="utf-8") as f:
            json.dump(self.graph, f, indent=2)

    def get_graph(self):
        return self.graph
