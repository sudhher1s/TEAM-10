"""
LLM-powered Reranker using OpenAI GPT-4
Advanced ranking with contextual understanding
"""
from __future__ import annotations
import os
from typing import Optional
from openai import OpenAI


class LLMReranker:
    """
    GPT-4 powered reranking for medical codes
    Uses advanced LLM for semantic understanding and ranking
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize LLM reranker with OpenAI API
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (gpt-4, gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        print(f"✓ LLMReranker initialized with {model}")

    def rerank(self, query: str, candidates: list[dict], top_n: int = 5) -> list[dict]:
        """
        Rerank candidates using GPT-4 semantic understanding
        
        Args:
            query: Original medical note/query
            candidates: List of dicts with 'code' and 'description'
            top_n: Number of results to return
            
        Returns: Reranked candidates with confidence scores
        """
        if not candidates:
            return []
        
        # Format candidates for LLM
        candidate_text = "\n".join([
            f"{i+1}. {c['code']}: {c['description']}"
            for i, c in enumerate(candidates[:20])  # Limit to top 20
        ])
        
        prompt = f"""You are an expert medical coder. Given a clinical note and candidate ICD-10 codes, 
rank them by relevance. Return ONLY a JSON array with top {top_n} codes with confidence scores (0-1).

Clinical Note:
{query[:2000]}

Candidate Codes:
{candidate_text}

Return JSON format:
[{{"code": "CODE", "confidence": 0.95, "reason": "brief explanation"}}]
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # More deterministic
                max_tokens=500
            )
            
            # Parse response
            import json
            result_text = response.choices[0].message.content
            
            # Extract JSON
            json_start = result_text.find("[")
            json_end = result_text.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                reranked = json.loads(json_str)
                return reranked[:top_n]
            
        except Exception as e:
            print(f"LLM reranking error: {e}")
        
        # Fallback to original order if LLM fails
        return [
            {
                "code": c["code"],
                "confidence": 0.8,
                "reason": "fallback"
            }
            for c in candidates[:top_n]
        ]

    def explain(self, query: str, code: str, description: str) -> str:
        """
        Generate explanation for why a code matches the query
        """
        prompt = f"""You are an expert medical coder. Briefly explain why the ICD-10 code {code} 
is appropriate for this clinical note:

Note: {query[:1000]}

Code: {code} - {description}

Provide a 1-2 sentence explanation."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Code match for: {description}"
