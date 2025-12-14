import sys
from pathlib import Path
import json

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_8_llm_grounding.src.llm_grounder import LLMGrounder


def test_llm_grounder_mock_basic():
    """Test LLM grounder mock mode works without API key."""
    grounder = LLMGrounder(model="gpt-3.5-turbo", provider="mock")
    
    evidence = [
        {
            "code": "I2101",
            "title": "STEMI involving left main coronary artery",
            "description": "ST elevation myocardial infarction of left main",
            "aliases": ["MI", "heart attack"]
        },
        {
            "code": "I2111",
            "title": "STEMI involving right coronary artery",
            "description": "ST elevation myocardial infarction of RCA",
            "aliases": ["Right coronary STEMI"]
        }
    ]
    
    # This uses mock response (no OpenAI key)
    result = grounder.ground(
        query="patient with chest pain and ST elevation",
        evidence=evidence
    )
    
    assert result.query == "patient with chest pain and ST elevation"
    assert len(result.codes) > 0
    assert 0.0 <= result.confidence <= 1.0
    assert result.elapsed_ms >= 0
    print(f"✓ Mock response test passed")
    print(f"  - Query: {result.query}")
    print(f"  - Codes: {result.codes}")
    print(f"  - Confidence: {result.confidence:.2%}")


def test_llm_grounder_prompt_building():
    """Test prompt construction."""
    grounder = LLMGrounder(provider="mock")
    
    evidence = [
        {"code": "A000", "title": "Cholera", "description": "Vibrio cholerae", "aliases": ["Cholera"]}
    ]
    violations = [
        {"severity": "WARNING", "message": "Code is unspecified"}
    ]
    
    prompt = grounder._build_prompt("cholera outbreak", evidence, violations)
    
    assert "cholera outbreak" in prompt.lower()
    assert "A000" in prompt
    assert "Cholera" in prompt
    assert "WARNING" in prompt
    assert "RETRIEVED RELEVANT ICD-10 CODES" in prompt
    print(f"✓ Prompt building test passed")


def test_llm_grounder_with_guardrails():
    """Test LLM grounder with guardrails validation."""
    grounder = LLMGrounder(model="gpt-3.5-turbo")
    
    evidence = [
        {"code": "I2101", "title": "STEMI left main", "description": "...", "aliases": []}
    ]
    
    guardrails_result = {
        "violations": [
            {"severity": "WARNING", "message": "Test warning"}
        ],
        "is_valid": True
    }
    
    result = grounder.ground_with_guardrails(
        "chest pain",
        evidence,
        guardrails_result
    )
    
    assert result.query == "chest pain"
    assert len(result.warnings) > 0
    assert result.is_safe == True
    assert result.llm_response is not None
    print(f"✓ Guardrails integration test passed")
    print(f"  - Is safe: {result.is_safe}")
    print(f"  - Warnings: {result.warnings}")
