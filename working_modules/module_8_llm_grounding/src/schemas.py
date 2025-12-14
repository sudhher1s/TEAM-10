from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class LLMResponse:
    """LLM-generated grounded response."""
    query: str
    response_text: str
    codes: List[str]  # Recommended codes
    explanation: str  # Why these codes
    confidence: float  # 0.0-1.0
    citations: List[str]  # References to evidence
    elapsed_ms: float
    model_used: str
    
@dataclass
class GroundedResult:
    """Complete grounding result with LLM output."""
    query: str
    llm_response: LLMResponse
    is_safe: bool  # Passed guardrails
    warnings: List[str]  # Policy warnings
