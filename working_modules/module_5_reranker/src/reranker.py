"""
Module 5: Cross-Encoder Reranker
Re-scores candidate codes using a cross-encoder trained on MS MARCO.
"""
import time
from dataclasses import asdict
from typing import List

from .schemas import RerankedItem, RerankResults

try:
    from sentence_transformers import CrossEncoder
except Exception:
    CrossEncoder = None

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if CrossEncoder is None:
            raise ImportError("sentence-transformers not installed. pip install sentence-transformers")
        self.model_name = model_name
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: List[dict], top_k: int = 10) -> RerankResults:
        """
        candidates: list of dicts with keys {code, title, category, index_id}
        Returns top_k re-scored by cross-encoder.
        """
        t0 = time.time()
        pairs = [(query, f"{c.get('title','')} [{c.get('code','')}]") for c in candidates]
        scores = self.model.predict(pairs)
        enriched = []
        for c, s in zip(candidates, scores):
            enriched.append(RerankedItem(
                code=c.get("code"),
                title=c.get("title"),
                category=c.get("category"),
                score=float(s),
                index_id=int(c.get("index_id", -1)),
            ))
        enriched.sort(key=lambda x: x.score, reverse=True)
        result_items = enriched[:top_k]
        elapsed_ms = (time.time() - t0) * 1000.0
        return RerankResults(query=query, items=result_items, elapsed_ms=elapsed_ms)
