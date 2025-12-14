"""
Module 8.2: Google LLM Grounding (Gemini)
Provides a Gemini-based grounding path using GOOGLE_API_KEY.
Falls back to mock/offline mode when the key or client is unavailable.
"""
import os
import json
import time
from typing import List, Optional, Dict

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from working_modules.module_8_llm_grounding.src.schemas import LLMResponse, GroundedResult


class GoogleGrounder:
    """Generates grounded responses using Google Gemini, with safe mock fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        provider: str = "google",
    ):
        # Downgrade to mock if google SDK is missing
        if provider == "google" and genai is None:
            provider = "mock"

        key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.provider = provider
        self.client = None

        if self.provider == "google":
            if not key:
                # No key available; stay safe in mock mode
                self.provider = "mock"
            else:
                try:
                    genai.configure(api_key=key)
                    self.client = genai
                except Exception:
                    # Any init failure -> mock
                    self.provider = "mock"
                    self.client = None

    def _build_prompt(self, query: str, evidence: List[Dict], violations: List[Dict] = None) -> str:
        evidence_text = ""
        for i, ev in enumerate(evidence, 1):
            evidence_text += f"\n{i}. {ev.get('code', '')} - {ev.get('title', '')}\n"
            if ev.get("description"):
                evidence_text += f"   Description: {ev['description']}\n"
            if ev.get("aliases"):
                evidence_text += f"   Also known as: {', '.join(ev['aliases'])}\n"

        warnings_text = ""
        if violations:
            warnings_text = "\nCOMPLIANCE WARNINGS:\n"
            for v in violations:
                warnings_text += f"- [{v.get('severity', 'INFO')}] {v.get('message', '')}\n"

        prompt = f"""You are an expert medical coding assistant. Recommend ICD-10 codes based on the evidence.

USER QUERY: {query}

RETRIEVED RELEVANT ICD-10 CODES:
{evidence_text}
{warnings_text}

Return JSON with keys: codes (list), explanations (dict), confidence (int 0-100), summary (str).
"""
        return prompt

    def _mock_response(self, query: str, evidence: List[Dict]) -> LLMResponse:
        sorted_ev = sorted(evidence, key=lambda ev: float(ev.get("relevance_score", 0.0)), reverse=True)
        top = sorted_ev[:3] if sorted_ev else evidence[:3]
        codes = [ev.get("code", "") for ev in top]

        if top:
            avg_score = sum(float(ev.get("relevance_score", 0.0)) for ev in top) / len(top)
            base_confidence = min(0.9, max(0.3, avg_score * 0.8))
            confidence_pct = int(base_confidence * 100)
        else:
            base_confidence = 0.45
            confidence_pct = 45

        expl_lines = []
        for i, ev in enumerate(top, 1):
            code = ev.get("code", "")
            title = ev.get("title", "")
            desc = ev.get("description", "")
            score = float(ev.get("relevance_score", 0.0))
            code_conf = max(30, min(95, int(score * 100 * (1 - i * 0.15))))
            reason = f"{i}. {code} — {title} [{code_conf}% match]\n"
            if desc:
                reason += f"   Clinical Description: {desc[:250]}{'...' if len(desc) > 250 else ''}\n"
            reason += f"   Relevance Score: {score:.3f}\n"
            reason += "   Rationale: Selected based on semantic similarity and clinical context alignment.\n"
            expl_lines.append(reason)

        summary = (
            f"Based on: '{query[:80]}{'...' if len(query) > 80 else ''}'\n\n"
            + "Recommended ICD-10 codes:\n\n"
            + "\n".join(expl_lines)
            + f"\nOverall Confidence: {confidence_pct}% (offline mock)\n"
            + "Model: Evidence-Based Rule Engine (Mock)\n"
        )

        return LLMResponse(
            query=query,
            response_text=summary,
            codes=codes,
            explanation=summary,
            confidence=base_confidence,
            citations=[ev.get("code", "") for ev in top],
            elapsed_ms=0.0,
            model_used=f"mock",
        )

    def ground(self, query: str, evidence: List[Dict], violations: List[Dict] = None, temperature: float = 0.3) -> LLMResponse:
        # Mock path
        if self.provider != "google" or self.client is None:
            return self._mock_response(query, evidence)

        t0 = time.time()
        prompt = self._build_prompt(query, evidence, violations)

        try:
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt, generation_config={"temperature": temperature})
            content = getattr(response, "text", None) or str(response)
            elapsed_ms = (time.time() - t0) * 1000.0

            # Parse JSON if present
            try:
                data = json.loads(content)
                codes = data.get("codes", []) if isinstance(data.get("codes", []), list) else []
                confidence = data.get("confidence", 50)
                confidence = confidence / 100.0 if isinstance(confidence, (int, float)) else 0.5
                summary = data.get("summary", content)
            except json.JSONDecodeError:
                codes = []
                confidence = 0.5
                summary = content

            return LLMResponse(
                query=query,
                response_text=content,
                codes=codes,
                explanation=summary,
                confidence=confidence,
                citations=[ev.get("code", "") for ev in evidence[:3]],
                elapsed_ms=elapsed_ms,
                model_used=f"{self.model} (Gemini)",
            )
        except Exception as e:
            print(f"Gemini API error: {e}, falling back to mock")
            return self._mock_response(query, evidence)

    def ground_with_guardrails(self, query: str, evidence: List[Dict], guardrails_result: Dict) -> GroundedResult:
        violations = guardrails_result.get("violations", [])
        is_valid = guardrails_result.get("is_valid", True)
        llm_response = self.ground(query, evidence, violations)

        warnings = []
        for v in violations:
            warnings.append(f"[{v.get('severity', 'INFO')}] {v.get('message', '')}")

        return GroundedResult(
            query=query,
            llm_response=llm_response,
            is_safe=is_valid,
            warnings=warnings,
        )
