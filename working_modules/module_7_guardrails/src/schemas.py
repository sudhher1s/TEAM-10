from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PolicyViolation:
    """A single policy violation or flag."""
    rule_id: str
    rule_name: str
    code: str
    severity: SeverityLevel
    message: str
    recommendation: Optional[str] = None

@dataclass
class GuardrailsResult:
    """Result of guardrails validation."""
    query: str
    codes: List[str]
    violations: List[PolicyViolation]
    is_valid: bool  # True if no critical violations
    elapsed_ms: float
