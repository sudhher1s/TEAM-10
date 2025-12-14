"""
Module 6: Evidence Extraction
Retrieves rich context (title, description, aliases, category) for each code
from the knowledge base, providing grounding context for LLM responses.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

from .schemas import Evidence, EvidenceSet

class EvidenceExtractor:
    """Extracts evidence/context for retrieved codes from the KB."""
    
    def __init__(self, kb_path: Path):
        """
        Initialize with knowledge base.
        
        Args:
            kb_path: Path to kb.json from Module 1
        """
        self.kb_path = kb_path
        self.kb = self._load_kb()
        self.code_to_item = {item["code"]: item for item in self.kb}
    
    def _load_kb(self) -> List[Dict]:
        """Load KB from JSON."""
        with open(self.kb_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def extract(
        self,
        query: str,
        reranked_items: List[Dict],
    ) -> EvidenceSet:
        """
        Extract evidence for reranked items.
        
        Args:
            query: Original user query
            reranked_items: List of dicts with keys {code, title, score, index_id, ...}
            
        Returns:
            EvidenceSet with rich context for each item
        """
        t0 = time.time()
        evidence_list: List[Evidence] = []
        
        for item in reranked_items:
            code = item.get("code")
            score = item.get("score", 0.0)
            
            kb_item = self.code_to_item.get(code)
            if kb_item is None:
                continue
            
            ev = Evidence(
                code=code,
                title=kb_item.get("title", ""),
                description=kb_item.get("description", ""),
                category=kb_item.get("category", ""),
                aliases=kb_item.get("aliases", []),
                relevance_score=float(score),
            )
            evidence_list.append(ev)
        
        elapsed_ms = (time.time() - t0) * 1000.0
        return EvidenceSet(query=query, items=evidence_list, elapsed_ms=elapsed_ms)
