import sys
from pathlib import Path

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_7_guardrails.src.guardrails_checker import GuardrailsChecker
from working_modules.module_7_guardrails.src.schemas import SeverityLevel


def test_guardrails_valid_codes():
    """Test guardrails with valid, specific codes."""
    checker = GuardrailsChecker()
    result = checker.check(
        query="myocardial infarction",
        codes=["I2101", "I2111", "R0602"],
        titles=["STEMI involving left main coronary", 
                "STEMI involving right coronary",
                "Dyspnea"]
    )
    
    assert result.is_valid, f"Expected valid result, got violations: {result.violations}"
    assert len(result.violations) == 0, f"Expected no violations, got: {result.violations}"


def test_guardrails_unspecified_flag():
    """Test guardrails detects unspecified codes."""
    checker = GuardrailsChecker()
    result = checker.check(
        query="chest pain",
        codes=["R072"],
        titles=["Chest pain, unspecified"]
    )
    
    assert not result.is_valid or len(result.violations) > 0, "Expected warning for unspecified code"
    warnings = [v for v in result.violations if v.severity == SeverityLevel.WARNING]
    assert len(warnings) > 0, "Expected at least one warning"


def test_guardrails_category_limit():
    """Test guardrails enforces category code limits."""
    checker = GuardrailsChecker()
    # 5+ circulatory codes exceeds recommended limit
    result = checker.check(
        query="cardiovascular conditions",
        codes=["I2101", "I2111", "I2121", "I2131", "I2141", "I2151"],
        titles=["STEMI left main", "STEMI right", "STEMI left circumflex",
                "STEMI LAD", "STEMI other", "STEMI unspecified"]
    )
    
    violations = [v for v in result.violations if "Category Code Limit" in v.rule_name]
    assert len(violations) > 0, "Expected warning for exceeding category code limit"


def test_guardrails_format_validation():
    """Test guardrails detects invalid code format."""
    checker = GuardrailsChecker()
    result = checker.check(
        query="test query",
        codes=["", "X"],  # Invalid codes
        titles=["", ""]
    )
    
    errors = [v for v in result.violations if v.severity == SeverityLevel.ERROR]
    assert len(errors) > 0, "Expected error for invalid code format"
