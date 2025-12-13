from __future__ import annotations
from typing import Dict, List
import time
from .icd10_kb import build_kb
from .retrieval import BM25Retriever
from .reranker import Reranker
from .evidence_extractor import extract_spans
from .guardrails import is_safe_note, disclaimer, constrain_to_kb


class Predictor:
    def __init__(self):
        self.kb: list[dict] | None = None
        self.retriever = BM25Retriever()
        self.reranker = Reranker()

    def load(self):
        self.kb = build_kb()
        self.retriever.fit(self.kb)

    def predict(self, note_text: str, top_k: int = 5) -> Dict:
        safe, reason = is_safe_note(note_text)
        start = time.time()
        if not safe:
            return {
                "top_k": top_k,
                "predictions": [],
                "latency_ms": int((time.time() - start) * 1000),
                "safety": {"disclaimer": disclaimer(), "checks_passed": False, "reason": reason},
            }
        hits = self.retriever.search(note_text, top_n=50)
        # Convert to candidate dicts
        candidates: List[Dict] = []
        assert self.kb is not None
        for idx, score in hits:
            item = self.kb[idx]
            candidates.append({
                "icd10_code": item.get("icd10_code"),
                "title": item.get("title"),
                "description": item.get("description"),
                "category": item.get("category"),
                "score": float(score),
            })
        reranked = self.reranker.rerank(note_text, candidates, top_k=top_k)
        kb_codes = set([row.get("icd10_code") for row in self.kb])
        reranked = constrain_to_kb(reranked, kb_codes)
        # Evidence spans: pick key phrases from title/description
        outputs = []
        for r in reranked:
            keywords = []
            keywords.extend(r.get("title", "").split()[:3])
            keywords.extend(r.get("description", "").split()[:3])
            spans = extract_spans(note_text, keywords)[:3]
            outputs.append({
                "icd10_code": r["icd10_code"],
                "title": r["title"],
                "score": round(float(r.get("rerank_score", r.get("score", 0))), 4),
                "evidence_spans": spans,
                "explanation": f"Matched symptoms/phrases: {', '.join(spans)}",
            })
        return {
            "top_k": top_k,
            "predictions": outputs,
            "latency_ms": int((time.time() - start) * 1000),
            "safety": {"disclaimer": disclaimer(), "checks_passed": True},
        }
