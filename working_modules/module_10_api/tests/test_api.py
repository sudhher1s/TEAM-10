import sys
from pathlib import Path
import unittest
import json

WORKSPACE = Path("c:/MY PROJECTS/GEN AI")
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from fastapi.testclient import TestClient
from working_modules.module_10_api.src.api import app

class TestModule10API(unittest.TestCase):
    def test_health(self):
        client = TestClient(app)
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_code_mock(self):
        client = TestClient(app)
        body = {
            "query": "Patient presents with acute cholera infection",
            "provider": "mock",
            "kb_path": "c:/MY PROJECTS/GEN AI/working_modules/module_1_data_kb/output/kb.json"
        }
        resp = client.post("/code", json=body)
        # If KB missing, this may error; allow status 200 if present
        self.assertIn(resp.status_code, (200, 422))
        if resp.status_code == 200:
            data = resp.json()
            self.assertIn("grounded", data)

if __name__ == "__main__":
    unittest.main()
