from __future__ import annotations
from typing import List, Dict
from .config import settings


class Reranker:
    def __init__(self):
        pass

    def rerank(self, query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
        # Simple keyword-overlap reranker (pure Python)
        scored = []
        q_tokens = set(query.lower().split())
        for c in candidates:
            text_tokens = (c.get("title", "") + " " + c.get("description", "")).lower().split()
            overlap = len(q_tokens.intersection(text_tokens))
            scored.append({**c, "rerank_score": c.get("score", 0) + float(settings.rerank_overlap_weight) * overlap})
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored[:top_k]
