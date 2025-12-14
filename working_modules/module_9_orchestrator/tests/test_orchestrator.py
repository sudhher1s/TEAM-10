import os
import sys
from pathlib import Path
import unittest

# Ensure workspace root is on sys.path for absolute imports
WORKSPACE = Path("c:/MY PROJECTS/GEN AI")
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator

WORKSPACE = Path("c:/MY PROJECTS/GEN AI")

class TestModule9Orchestrator(unittest.TestCase):
    def setUp(self):
        # Paths based on prior modules' outputs. Adjust as needed.
        self.index_path = WORKSPACE / "working_modules/module_3_vector_index/index.faiss"
        self.item_metadata = WORKSPACE / "working_modules/module_2_embeddings/item_metadata.json"
        self.kb_path = WORKSPACE / "working_modules/module_6_evidence/kb.json"

    def test_mock_run(self):
        # Ensure files exist or skip test
        missing = [p for p in [self.index_path, self.item_metadata, self.kb_path] if not p.exists()]
        if missing:
            self.skipTest(f"Missing dependencies: {missing}")

        orchestrator = MedicalCodingOrchestrator(
            index_path=self.index_path,
            item_metadata_path=self.item_metadata,
            kb_path=self.kb_path,
            llm_provider="mock",
        )
        res = orchestrator.run("Patient presents with acute cholera infection", retrieve_k=50, rerank_k=5)
        self.assertIn("grounded", res)
        self.assertTrue(res["grounded"]["is_safe"])  # mock should generally be safe
        self.assertIsInstance(res["grounded"]["confidence"], float)


if __name__ == "__main__":
    unittest.main()
