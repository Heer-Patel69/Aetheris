import hmac
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add src/ to python path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from microservice.router import app, WEBHOOK_SECRET
from microservice.database import SessionLocal, WebhookDelivery, init_db
from microservice.dashboard import TelemetryDashboard

class TestWebhookMicroservice(unittest.TestCase):
    def setUp(self):
        init_db()
        self.db = SessionLocal()
        # Ensure fresh database state by clearing records
        self.db.query(WebhookDelivery).delete()
        self.db.commit()
        self.client = TestClient(app)

    def tearDown(self):
        self.db.close()
        # Clean rate limiter cache between runs
        from microservice.router import ip_rate_limit_cache
        ip_rate_limit_cache.clear()

    def test_missing_signature_header(self):
        """Expect HTTP 401 Unauthorized when signature header is missing."""
        response = self.client.post("/webhook", content="test-payload")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Missing cryptographic verification signature header", response.json()["detail"])

    def test_invalid_signature_verification(self):
        """Expect HTTP 403 Forbidden when signature is incorrect."""
        headers = {"X-Webhook-Signature": "invalid-sig-hash"}
        response = self.client.post("/webhook", content="test-payload", headers=headers)
        self.assertEqual(response.status_code, 403)
        
        # Verify it was logged in SQLite as failed
        logged = self.db.query(WebhookDelivery).filter(WebhookDelivery.processing_status == "failed").first()
        self.assertIsNotNone(logged)
        self.assertEqual(logged.payload, "test-payload")

    def test_valid_signature_verification(self):
        """Expect HTTP 200 OK when HMAC signature matches."""
        payload = b'{"event": "deployment_success", "id": 999}'
        valid_sig = hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
        
        headers = {"X-Webhook-Signature": valid_sig}
        response = self.client.post("/webhook", content=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        # Verify it was logged in SQLite as verified
        logged = self.db.query(WebhookDelivery).filter(WebhookDelivery.processing_status == "verified").first()
        self.assertIsNotNone(logged)
        self.assertIn("deployment_success", logged.payload)

    def test_secure_headers_presence(self):
        """Verify that strict security hardening headers are injected in HTTP responses."""
        payload = b"test-payload"
        valid_sig = hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
        headers = {"X-Webhook-Signature": valid_sig}
        
        response = self.client.post("/webhook", content=payload, headers=headers)
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("default-src 'self'", response.headers.get("Content-Security-Policy"))

    def test_ip_rate_limiting(self):
        """Verify that rate limiter returns HTTP 429 on exceeding max requests."""
        payload = b"payload"
        valid_sig = hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
        headers = {"X-Webhook-Signature": valid_sig}

        # Make 5 allowed requests
        for _ in range(5):
            response = self.client.post("/webhook", content=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

        # 6th request should fail with HTTP 429 Too Many Requests
        response = self.client.post("/webhook", content=payload, headers=headers)
        self.assertEqual(response.status_code, 429)

    def test_dashboard_renderer(self):
        """Verify dashboard rendering queries metrics successfully and loads styles."""
        # Log a test verified delivery
        delivery = WebhookDelivery(
            payload="test-dashboard",
            source_ip_hash="abc123hash",
            signature="sig",
            processing_status="verified"
        )
        self.db.add(delivery)
        self.db.commit()

        dashboard = TelemetryDashboard(os.getcwd())
        # Verify it runs without error
        dashboard.render()

if __name__ == "__main__":
    unittest.main()
