import os

# Exhaustive sections for standard engineering documents
STANDARD_SECTIONS = [
    "1. Purpose", "2. Background", "3. Problem Statement", "4. Business Context", 
    "5. Goals", "6. Non Goals", "7. Architecture", "8. Design Decisions", 
    "9. Reasoning", "10. Trade-offs", "11. Implementation Strategy", "12. Data Flow", 
    "13. Control Flow", "14. Execution Flow", "15. Dependencies", "16. Constraints", 
    "17. Assumptions", "18. Failure Cases", "19. Error Handling", "20. Recovery Strategy", 
    "21. Performance Considerations", "22. Security Considerations", "23. Scalability", 
    "24. Maintainability", "25. Future Improvements", "26. Risks", "27. Examples", 
    "28. Engineering Notes", "29. References", "30. Conclusion"
]

# Additional specific sections for Architecture documents
ARCHITECTURE_SECTIONS = [
    "High-level Architecture", "Low-level Architecture", "Components", "Responsibilities",
    "Communication", "Event Flow", "Request Flow", "Module Relationships", "Design Patterns", 
    "Alternatives", "Future Evolution"
]

class DocumentationGenerator:
    """
    Handles dynamic generation of exhaustive project documentation based on codebase state.
    Enforces the Aetheris Engineering Documentation Core Philosophy.
    """
    def __init__(self, project_root, aetheris_dir):
        self.project_root = project_root
        self.aetheris_dir = aetheris_dir
        
        self.docs_map = {
            "planning": ["PRD.md", "BRD.md", "Roadmap.md", "Milestones.md", "Tasks.md", "Risks.md", "TechnicalDebt.md"],
            "architecture": ["TRD.md", "Architecture.md", "SystemDesign.md", "Backend.md", "Frontend.md", "Database.md", "API.md", "Authentication.md", "Authorization.md", "Security.md", "Performance.md", "Scalability.md", "DevOps.md", "CI-CD.md", "Infrastructure.md"],
            "docs": ["UI.md", "UX.md", "DesignSystem.md", "Components.md", "UserFlows.md", "Wireframes.md"],
            "verification": ["Testing.md", "UnitTesting.md", "IntegrationTesting.md", "E2ETesting.md", "LoadTesting.md", "PerformanceTesting.md", "SecurityTesting.md", "Review.md", "Verification.md", "BugLog.md", "Changelog.md"],
            "runtime": ["Memory.md", "Replay.md"],
            "assets": ["Assets.md"]
        }

    def generate_all(self, discovery_state, knowledge_graph):
        """Generates or updates all documentation files."""
        for folder, files in self.docs_map.items():
            folder_path = os.path.join(self.aetheris_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            for file in files:
                filepath = os.path.join(folder_path, file)
                self._generate_or_update(filepath, file, folder, discovery_state, knowledge_graph)
                
    def _generate_or_update(self, filepath, filename, folder, state, kg):
        """
        Generates exhaustive content ensuring NO shallow documentation.
        Answers WHAT, WHY, HOW, WHEN, WHERE, WHO, WHAT IF.
        """
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {filename.replace('.md', '')}\n\n")
                f.write("> **Aetheris Engineering Source of Truth**\n")
                f.write("> This document is generated and maintained to provide an exhaustive, senior-level engineering explanation.\n")
                f.write("> It answers WHAT, WHY, HOW, WHEN, WHERE, WHO, and WHAT IF for every decision.\n\n")
                
                # Use architecture specific sections if it's in the architecture folder
                sections_to_use = STANDARD_SECTIONS.copy()
                if folder == "architecture":
                    # Inject architecture specific sections into the appropriate place (e.g. after Architecture)
                    idx = sections_to_use.index("7. Architecture") + 1
                    for i, arch_sec in enumerate(ARCHITECTURE_SECTIONS):
                        sections_to_use.insert(idx + i, f"7.{i+1} {arch_sec}")

                for section in sections_to_use:
                    f.write(f"## {section}\n\n")
                    f.write(f"<!-- EXPLAIN EVERYTHING: Provide deep engineering insight for '{section}'. -->\n")
                    f.write("<!-- Cover WHY this exists, HOW it works, ALTERNATIVES considered, and FAILURE cases. -->\n\n")
                    
                    if filename == "Architecture.md" and section == "7. Architecture":
                        f.write(f"**Detected Python:** {state.get('is_python')}\n")
                        f.write(f"**Detected Node.js:** {state.get('is_node')}\n")
                        f.write(f"\n**Total detected components:** {len(kg.get('classes', []))}\n\n")
                    elif section == "30. Conclusion":
                        f.write("<!-- Internal Review Checklist:\n")
                        f.write("- Can a new engineer understand the entire system from this document?\n")
                        f.write("- Are all trade-offs and alternatives explained?\n")
                        f.write("- Are failure modes explicitly stated? -->\n\n")
        else:
            # We don't overwrite user work, but we ensure the intelligence engine can 
            # dynamically update existing documentation in a non-destructive manner later.
            pass
