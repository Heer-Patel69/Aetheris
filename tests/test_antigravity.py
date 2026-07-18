import sys
import unittest
from pathlib import Path

# Add scripts directory to path to allow importing antigravity_planner
scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

import antigravity_planner

class TestAntiGravityPlanner(unittest.TestCase):
    def test_analyze_domain_ecommerce(self):
        divs = antigravity_planner.analyze_domain("Build an E-commerce Platform")
        self.assertIn("product", divs)
        self.assertIn("engineering", divs)
        self.assertIn("design", divs)
        self.assertIn("marketing", divs)
        self.assertIn("sales", divs)

    def test_analyze_domain_saas(self):
        divs = antigravity_planner.analyze_domain("Create a Multi-tenant SaaS Platform")
        self.assertIn("engineering", divs)
        self.assertIn("product", divs)
        self.assertIn("security", divs)
        self.assertIn("project-management", divs)

    def test_analyze_domain_ai(self):
        divs = antigravity_planner.analyze_domain("Develop an AI Product with Agentic capabilities")
        self.assertIn("aetheris", divs)
        self.assertIn("engineering", divs)
        self.assertIn("specialized", divs)

    def test_map_skills(self):
        # Create mock skills list
        mock_skills = {
            "skill1": {"id": "skill1", "name": "Skill 1", "division": "engineering", "type": "agency"},
            "skill2": {"id": "skill2", "name": "Skill 2", "division": "design", "type": "agency"},
            "core1": {"id": "core1", "name": "Core 1", "division": "core", "type": "core"}
        }
        
        active_divs = ["engineering"]
        skills = antigravity_planner.map_skills(active_divs, mock_skills)
        
        # Core skills should always be loaded, and engineering skills should be loaded
        ids = [s["id"] for s in skills]
        self.assertIn("core1", ids)
        self.assertIn("skill1", ids)
        self.assertNotIn("skill2", ids)

if __name__ == "__main__":
    unittest.main()
