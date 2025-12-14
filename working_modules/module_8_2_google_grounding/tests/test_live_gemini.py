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

def test_live_gemini_with_key():
    """Test actual Gemini grounding with GOOGLE_API_KEY set."""
    g = GoogleGrounder(provider="google")
    
    print(f"Provider: {g.provider}")
    print(f"Model: {g.model}")
    print(f"Client initialized: {g.client is not None}")
    
    res = g.ground("chest pain with ST elevation", evidence_sample)
    
    print(f"\n--- LLM Response ---")
    print(f"Query: {res.query}")
    print(f"Codes: {res.codes}")
    print(f"Confidence: {res.confidence:.2%}")
    print(f"Model: {res.model_used}")
    print(f"Elapsed: {res.elapsed_ms:.1f}ms")
    print(f"\nExplanation:\n{res.explanation[:800]}")
    print(f"\nFull Response:\n{res.response_text}")
    
    # Gemini successfully called (not mock)
    assert "Gemini" in res.model_used or "gemini" in res.model_used.lower()
    assert 0.0 <= res.confidence <= 1.0
    assert res.response_text  # Got a response
    print("\n✓ Live Gemini API working successfully!")


if __name__ == "__main__":
    test_live_gemini_with_key()
