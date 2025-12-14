import sys
from pathlib import Path

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_8_2_google_grounding.src.google_grounder import GoogleGrounder

evidence_sample = [
    {
        "code": "I2101",
        "title": "STEMI involving left main coronary artery",
        "description": "ST elevation myocardial infarction of left main",
        "aliases": ["MI", "heart attack"],
        "relevance_score": 0.87,
    },
    {
        "code": "I2111",
        "title": "STEMI involving right coronary artery",
        "description": "ST elevation myocardial infarction of RCA",
        "aliases": ["STEMI"],
        "relevance_score": 0.81,
    },
]

def test_mock_path_without_key():
    g = GoogleGrounder(provider="mock")
    res = g.ground("chest pain with ST elevation", evidence_sample)
    assert res.codes
    assert 0.0 <= res.confidence <= 1.0


def test_guardrails_wrapper():
    g = GoogleGrounder(provider="mock")
    guard = {"violations": [{"severity": "WARNING", "message": "Test warn"}], "is_valid": True}
    res = g.ground_with_guardrails("test", evidence_sample, guard)
    assert res.is_safe is True
    assert res.warnings
    assert res.llm_response is not None
