import os

DIAGRAM_SECTIONS = [
    "Purpose", "Explanation", "Components", "Relationships", 
    "Execution", "Examples", "Edge Cases", "Engineering Notes"
]

class DiagramGenerator:
    """
    Generates MermaidJS diagrams for the project architecture.
    Enforces the Aetheris Engineering Documentation Core Philosophy for diagrams.
    """
    def __init__(self, project_root, aetheris_dir):
        self.project_root = project_root
        self.aetheris_dir = aetheris_dir
        self.diagrams_dir = os.path.join(self.aetheris_dir, "diagrams")
        os.makedirs(self.diagrams_dir, exist_ok=True)

    def generate_all(self, knowledge_graph):
        """Generates all diagrams."""
        self._generate_system_architecture(knowledge_graph)
        self._generate_class_diagram(knowledge_graph)
        self._generate_dependency_graph(knowledge_graph)
        self._generate_er_diagram(knowledge_graph)

    def _write_diagram_template(self, filepath, title, mermaid_code):
        if os.path.exists(filepath):
            return
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write("> **Aetheris Engineering Source of Truth**\n")
            f.write("> Generating a diagram is NOT enough. Every diagram must include exhaustive explanations.\n\n")
            
            f.write("## Diagram\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_code)
            f.write("\n```\n\n")
            
            for section in DIAGRAM_SECTIONS:
                f.write(f"## {section}\n\n")
                f.write(f"<!-- Provide deep engineering insight for the '{section}' of this diagram. -->\n")
                f.write(f"<!-- Detail the WHAT, WHY, HOW, WHEN, WHERE, WHO, and WHAT IF. -->\n\n")

    def _generate_system_architecture(self, kg):
        filepath = os.path.join(self.diagrams_dir, "SystemArchitecture.md")
        mermaid = "graph TD\n  Client --> API\n  API --> DB[(Database)]"
        self._write_diagram_template(filepath, "System Architecture", mermaid)

    def _generate_class_diagram(self, kg):
        filepath = os.path.join(self.diagrams_dir, "ClassDiagram.md")
        mermaid = "classDiagram\n"
        for cls in kg.get("classes", []):
            mermaid += f"  class {cls}\n"
        if not kg.get("classes"):
            mermaid += "  class System\n"
        self._write_diagram_template(filepath, "Class Diagram", mermaid)

    def _generate_dependency_graph(self, kg):
        filepath = os.path.join(self.diagrams_dir, "DependencyGraph.md")
        mermaid = "graph LR\n  App --> Core"
        self._write_diagram_template(filepath, "Dependency Graph", mermaid)

    def _generate_er_diagram(self, kg):
        filepath = os.path.join(self.diagrams_dir, "ERDiagram.md")
        mermaid = "erDiagram\n  USER ||--o{ POST : writes\n  POST { string title\n         string body }"
        self._write_diagram_template(filepath, "Entity Relationship Diagram", mermaid)
