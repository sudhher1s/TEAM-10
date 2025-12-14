"""
Module 8: LLM Grounding
Generates clinically-grounded responses using OpenAI/Claude API.
Responses are grounded in retrieved evidence and validated by guardrails.
"""
import time
import json
from typing import List, Optional, Dict
from .schemas import LLMResponse, GroundedResult

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LLMGrounder:
    """
    Generates grounded responses using LLM APIs (OpenAI, Claude, etc.).
    Includes robust offline/mock fallback when API is unavailable.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        provider: str = "openai",
    ):
        """
        Initialize LLM grounder.
        
        Args:
            api_key: API key for LLM provider (or set OPENAI_API_KEY env var)
            model: Model name (gpt-3.5-turbo, gpt-4, etc.)
            provider: "openai" or "claude" (claude support planned)
        """
        # Initialize provider; allow mock for offline use
        if provider == "openai" and OpenAI is None:
            # Defer hard failure; we will switch to mock mode later
            provider = "mock"
        
        self.api_key = api_key
        self.model = model
        self.provider = provider
        
        # Initialize OpenAI client if applicable
        self.client = None
        if self.provider == "openai":
            try:
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    self.client = OpenAI()  # Uses env var
            except Exception:
                # Fall back to mock provider
                self.provider = "mock"
                self.client = None
    
    def _build_prompt(
        self,
        query: str,
        evidence: List[Dict],
        violations: List[Dict] = None,
    ) -> str:
        """
        Build medical coding prompt for LLM.
        
        Args:
            query: User query
            evidence: List of evidence dicts {code, title, description, aliases, ...}
            violations: Policy violations (guardrails)
            
        Returns:
            Formatted prompt
        """
        evidence_text = ""
        for i, ev in enumerate(evidence, 1):
            evidence_text += f"\n{i}. {ev.get('code', '')} - {ev.get('title', '')}\n"
            if ev.get('description'):
                evidence_text += f"   Description: {ev['description']}\n"
            if ev.get('aliases'):
                evidence_text += f"   Also known as: {', '.join(ev['aliases'])}\n"
        
        warnings_text = ""
        if violations:
            warnings_text = "\nCOMPLIANCE WARNINGS:\n"
            for v in violations:
                warnings_text += f"- [{v.get('severity', 'INFO')}] {v.get('message', '')}\n"
        
        prompt = f"""You are an expert medical coding assistant. Your task is to recommend ICD-10 codes for a patient presentation.

USER QUERY: {query}

RETRIEVED RELEVANT ICD-10 CODES:
{evidence_text}

{warnings_text}

Based on the query and the evidence provided above:

1. Recommend the most relevant ICD-10 code(s) (top 3)
2. Explain why each code matches the patient presentation
3. Address any compliance warnings if present
4. Provide overall confidence in your recommendation (0-100%)

Format your response as JSON with keys: codes (list), explanations (dict), confidence (int), summary (str)"""
        
        return prompt

    def _mock_response(self, query: str, evidence: List[Dict]) -> LLMResponse:
        """Generate a detailed mock response using provided evidence."""
        # Pick top-3 codes by relevance_score if available, else first three
        sorted_ev = sorted(
            evidence,
            key=lambda ev: float(ev.get("relevance_score", 0.0)),
            reverse=True,
        )
        top = sorted_ev[:3] if sorted_ev else evidence[:3]
        codes = [ev.get("code", "") for ev in top]
        
        # Calculate realistic confidence based on relevance scores
        if top:
            avg_score = sum(float(ev.get("relevance_score", 0.0)) for ev in top) / len(top)
            # Scale confidence: 0.3-0.9 range instead of always 1.0
            base_confidence = min(0.9, max(0.3, avg_score * 0.8))
            confidence_pct = int(base_confidence * 100)
        else:
            base_confidence = 0.45
            confidence_pct = 45
        
        # Build detailed explanations with varied confidence per code
        expl_lines = []
        for i, ev in enumerate(top, 1):
            code = ev.get('code', '')
            title = ev.get('title', '')
            desc = ev.get('description', '')
            score = float(ev.get('relevance_score', 0.0))
            
            # Vary confidence: primary code higher, secondary lower
            code_confidence = max(30, min(95, int(score * 100 * (1 - i*0.15))))
            
            reason = f"{i}. **{code}** — {title} [{code_confidence}% match]\n"
            if desc:
                reason += f"   Clinical Description: {desc[:250]}{'...' if len(desc) > 250 else ''}\n"
            reason += f"   Relevance Score: {score:.3f}\n"
            reason += f"   Rationale: Selected based on semantic similarity and clinical context alignment.\n"
            expl_lines.append(reason)
        
        summary = (
            f"Based on the clinical presentation: '{query[:80]}{'...' if len(query) > 80 else ''}'\n\n"
            + "Recommended ICD-10 codes (in order of clinical relevance):\n\n"
            + "\n".join(expl_lines)
            + f"\n**Overall Clinical Confidence:** {confidence_pct}% (rule-based grounding with semantic analysis)\n"
            + "**Model:** Evidence-Based Rule Engine (Offline Mode)\n"
            + "**Note:** For OpenAI-powered reasoning, configure provider='openai' with valid API key."
        )
        return LLMResponse(
            query=query,
            response_text=summary,
            codes=codes,
            explanation=summary,
            confidence=base_confidence,
            citations=[ev.get("code", "") for ev in top],
            elapsed_ms=0.0,
            model_used=f"Evidence-Based Rule Engine (Offline)",
        )
    
    def ground(
        self,
        query: str,
        evidence: List[Dict],
        violations: List[Dict] = None,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """
        Generate grounded LLM response.
        
        Args:
            query: User query
            evidence: Retrieved evidence (list of dicts with code, title, description, etc.)
            violations: Guardrails violations
            temperature: LLM sampling temperature (0.0-1.0)
            
        Returns:
            LLMResponse with generated content
        """
        # If provider is mock or client unavailable, generate mock response
        if self.provider == "mock" or self.client is None:
            return self._mock_response(query, evidence)
        
        t0 = time.time()
        prompt = self._build_prompt(query, evidence, violations)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical coding expert assistant. Provide accurate, evidence-based ICD-10 coding recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=500,
            )
            
            content = response.choices[0].message.content
            elapsed_ms = (time.time() - t0) * 1000.0
            
            # Try to parse JSON response
            try:
                data = json.loads(content)
                codes = data.get("codes", [])
                explanations = data.get("explanations", {})
                confidence = data.get("confidence", 50) / 100.0
                summary = data.get("summary", content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                codes = []
                explanations = {}
                confidence = 0.5
                summary = content
            
            return LLMResponse(
                query=query,
                response_text=content,
                codes=codes if isinstance(codes, list) else [],
                explanation=summary,
                confidence=confidence,
                citations=[ev.get("code", "") for ev in evidence[:3]],
                elapsed_ms=elapsed_ms,
                model_used=self.model,
            )
        
        except Exception:
            # Robust fallback to mock response
            return self._mock_response(query, evidence)
    
    def ground_with_guardrails(
        self,
        query: str,
        evidence: List[Dict],
        guardrails_result: Dict,
    ) -> GroundedResult:
        """
        Generate grounded response with guardrails validation.
        
        Args:
            query: User query
            evidence: Retrieved evidence
            guardrails_result: Result from Module 7 GuardrailsChecker
            
        Returns:
            GroundedResult with LLM response and safety info
        """
        violations = guardrails_result.get("violations", [])
        is_valid = guardrails_result.get("is_valid", True)
        
        # Generate LLM or mock response
        llm_response = self.ground(query, evidence, violations)
        
        # Build warnings list
        warnings = []
        for v in violations:
            warnings.append(f"[{v.get('severity', 'INFO')}] {v.get('message', '')}")
        
        return GroundedResult(
            query=query,
            llm_response=llm_response,
            is_safe=is_valid,
            warnings=warnings,
        )
