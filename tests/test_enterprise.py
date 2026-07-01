import unittest
import shutil
from pathlib import Path
from enterprise import EnterprisePlatform

class TestEnterprise(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_enterprise_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.enterprise = EnterprisePlatform(self.workspace_path)

    def tearDown(self):
        shutil.rmtree(self.workspace_path, ignore_errors=True)

    def test_identity_auth(self):
        # Valid token
        res_valid = self.enterprise.authorize_request("secure-aetheris-token-2026", "execute")
        self.assertTrue(res_valid["authorized"])
        self.assertEqual(res_valid["user_id"], "usr-999")

        # Invalid token
        res_invalid = self.enterprise.authorize_request("bad-token", "execute")
        self.assertFalse(res_invalid["authorized"])
        self.assertEqual(res_invalid["user_id"], "usr-anonymous")

    def test_rbac_rules(self):
        # Viewer role trying to execute action
        res = self.enterprise.authorize_request("bad-token", "execute")
        self.assertFalse(res["authorized"])
        
        # Viewer role trying to read action
        res_read = self.enterprise.authorize_request("bad-token", "read")
        self.assertTrue(res_read["authorized"])

    def test_audit_logs(self):
        self.enterprise.authorize_request("secure-aetheris-token-2026", "execute")
        log_path = self.workspace_path / ".aetheris" / "audit_trail.log"
        self.assertTrue(log_path.exists())
        log_content = log_path.read_text(encoding="utf-8")
        self.assertIn("usr-999", log_content)
        self.assertIn("ALLOWED", log_content)
