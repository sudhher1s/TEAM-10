"""
Module 7: Guardrails & Compliance Checker
Applies medical coding standards, HIPAA rules, and clinical guidelines
to validate retrieved codes before LLM generation.
"""
import time
from typing import List, Dict, Optional, Set

from .schemas import PolicyViolation, GuardrailsResult, SeverityLevel

class GuardrailsChecker:
    """
    Validates medical codes against compliance rules and clinical guidelines.
    """
    
    def __init__(self):
        """Initialize guardrails with default rules."""
        self.rules = self._init_rules()
    
    def _init_rules(self) -> Dict:
        """Define medical coding and compliance rules."""
        return {
            # ICD-10 section rules
            "a00-b99": {
                "name": "Infectious Diseases",
                "max_codes": 3,
                "requires_specificity": True,
            },
            "i00-i99": {
                "name": "Circulatory System",
                "max_codes": 5,
                "requires_specificity": True,
            },
            "j00-j99": {
                "name": "Respiratory System",
                "max_codes": 4,
                "requires_specificity": True,
            },
            # Specificity rules (unspecified codes should be avoided if possible)
            "unspecified_codes": {
                "patterns": [
                    "unspecified",
                    "nos",  # not otherwise specified
                    "nec",  # not elsewhere classifiable
                ],
                "severity": "warning",
            },
            # Clinical coherence
            "incompatible_combinations": {
                # E.g., pregnancy-related codes with male-only codes
                "pregnancy": ["O00-O99"],
                "male_only": ["N40", "N45", "N50"],
            },
        }
    
    def _get_code_section(self, code: str) -> Optional[str]:
        """Extract section from ICD-10 code (e.g., 'A00' -> 'a00-b99')."""
        if not code or len(code) < 1:
            return None
        
        first_char = code[0].lower()
        first_three = code[:3].lower()
        
        # Map first character to section
        sections = {
            "a": "a00-b99",
            "b": "a00-b99",
            "c": "c00-d49",
            "d": "c00-d49",
            "e": "e00-e89",
            "f": "f00-f99",
            "g": "g00-g99",
            "h": "h00-h99",
            "i": "i00-i99",
            "j": "j00-j99",
            "k": "k00-k95",
            "l": "l00-l99",
            "m": "m00-m99",
            "n": "n00-n99",
            "o": "o00-o99",
            "p": "p00-p96",
            "q": "q00-q99",
            "r": "r00-r99",
            "s": "s00-t88",
            "t": "s00-t88",
            "u": "u00-u85",
            "v": "v00-y99",
            "w": "v00-y99",
            "x": "v00-y99",
            "y": "v00-y99",
            "z": "z00-z99",
        }
        return sections.get(first_char)
    
    def _check_specificity(self, code: str, title: str) -> Optional[PolicyViolation]:
        """Check if code is adequately specific."""
        title_lower = title.lower()
        unspec_patterns = self.rules["unspecified_codes"]["patterns"]
        
        for pattern in unspec_patterns:
            if pattern in title_lower:
                return PolicyViolation(
                    rule_id="specificity_001",
                    rule_name="Code Specificity",
                    code=code,
                    severity=SeverityLevel.WARNING,
                    message=f"Code '{code}' is unspecified (contains '{pattern}')",
                    recommendation="Consider using a more specific code if clinical details are available",
                )
        return None
    
    def _check_code_validity(self, code: str) -> Optional[PolicyViolation]:
        """Check if code format is valid."""
        # Basic ICD-10 format: letter + 2 digits + optional decimal + digits
        if not code or len(code) < 3:
            return PolicyViolation(
                rule_id="format_001",
                rule_name="Code Format Validation",
                code=code,
                severity=SeverityLevel.ERROR,
                message=f"Code '{code}' has invalid format",
                recommendation="Code must follow ICD-10 format (e.g., A00.0, I2101)",
            )
        
        if not code[0].isalpha():
            return PolicyViolation(
                rule_id="format_002",
                rule_name="Code Format Validation",
                code=code,
                severity=SeverityLevel.ERROR,
                message=f"Code '{code}' must start with a letter",
            )
        
        return None
    
    def _check_duplicate_categories(self, codes: List[str], titles: List[str]) -> List[PolicyViolation]:
        """Flag if multiple codes from same category are selected."""
        violations = []
        sections: Dict[str, List[str]] = {}
        
        for code, title in zip(codes, titles):
            section = self._get_code_section(code)
            if section:
                if section not in sections:
                    sections[section] = []
                sections[section].append(code)
        
        # Check against max_codes rule
        for section, section_codes in sections.items():
            if section in self.rules:
                max_codes = self.rules[section].get("max_codes")
                if max_codes and len(section_codes) > max_codes:
                    violations.append(PolicyViolation(
                        rule_id=f"max_codes_{section}",
                        rule_name="Category Code Limit",
                        code=f"{','.join(section_codes)}",
                        severity=SeverityLevel.WARNING,
                        message=f"Section {section} has {len(section_codes)} codes (max recommended: {max_codes})",
                        recommendation="Consider consolidating related codes",
                    ))
        
        return violations
    
    def check(
        self,
        query: str,
        codes: List[str],
        titles: List[str],
    ) -> GuardrailsResult:
        """
        Validate codes against guardrails.
        
        Args:
            query: Original user query
            codes: List of ICD-10 codes
            titles: List of code titles (parallel to codes)
            
        Returns:
            GuardrailsResult with violations and validity flag
        """
        t0 = time.time()
        violations: List[PolicyViolation] = []
        
        # Check each code
        for code, title in zip(codes, titles):
            # Format validation
            fmt_violation = self._check_code_validity(code)
            if fmt_violation:
                violations.append(fmt_violation)
            
            # Specificity check
            spec_violation = self._check_specificity(code, title)
            if spec_violation:
                violations.append(spec_violation)
        
        # Check category constraints
        category_violations = self._check_duplicate_categories(codes, titles)
        violations.extend(category_violations)
        
        # Determine overall validity (no critical errors)
        has_critical = any(v.severity == SeverityLevel.CRITICAL for v in violations)
        has_error = any(v.severity == SeverityLevel.ERROR for v in violations)
        is_valid = not (has_critical or has_error)
        
        elapsed_ms = (time.time() - t0) * 1000.0
        return GuardrailsResult(
            query=query,
            codes=codes,
            violations=violations,
            is_valid=is_valid,
            elapsed_ms=elapsed_ms,
        )
