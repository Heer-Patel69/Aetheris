import unittest
from organization import AIOrganizationManager, CEOAgent, CTOAgent, ArchitectAgent, DeveloperAgent

class TestOrganization(unittest.TestCase):
    def setUp(self):
        self.org = AIOrganizationManager()

    def test_ceo_alignment(self):
        ceo = CEOAgent()
        res = ceo.execute("Build a web scheduler application")
        self.assertEqual(res["decision"], "APPROVED")
        self.assertEqual(res["strategic_priority"], "HIGH")

    def test_cto_stack_selection(self):
        cto = CTOAgent()
        res = cto.execute({"decision": "APPROVED"})
        self.assertTrue(res["compliance"])
        self.assertIn("python", res["approved_stack"])

    def test_collaborative_workflow(self):
        session = self.org.run_collaborative_session("Build web scheduler")
        self.assertEqual(session["session_status"], "SUCCESS")
        self.assertIn("CEO", session["participants"])
        self.assertIn("src/main.py", session["artifacts"])
