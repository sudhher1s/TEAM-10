from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import re
from rank_bm25 import BM25Okapi
from .config import settings


STOPWORDS = {
    "a","an","the","and","or","of","for","to","with","in","on","at","by","is","are","was","were","be","as","this","that","these","those","x","days","day","patient","male","female","yo","hx","pmh","hpi","lab","labs","shows","show","noted","noting","not","very","mild","severe","moderate","pain","symptoms"  
}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    toks = [t for t in text.split() if len(t) > 1 and t not in STOPWORDS]
    return toks


@dataclass
class BM25Retriever:
    def __post_init__(self):
        self.docs: List[str] = []
        self.codes: List[str] = []
        self.bm25: BM25Okapi | None = None
        self._tokenized_docs: List[List[str]] = []

    def fit(self, kb: list[dict]) -> None:
        self.docs = [(str(item.get("title", "")) + " | " + str(item.get("description", "")).strip()) for item in kb]
        self.codes = [str(item.get("icd10_code", "")) for item in kb]
        # weight title tokens by duplicating them
        self._tokenized_docs = []
        for item in kb:
            title = str(item.get("title", ""))
            desc = str(item.get("description", ""))
            # title counted settings.title_weight_factor times
            toks = tokenize(desc) + sum([tokenize(title) for _ in range(max(1, int(settings.title_weight_factor)))], [])
            self._tokenized_docs.append(toks)
        self.bm25 = BM25Okapi(self._tokenized_docs)

    def search(self, query: str, top_n: int = 50) -> List[Tuple[int, float]]:
        if self.bm25 is None:
            raise RuntimeError("Retriever not fitted")
        q_tokens = tokenize(query)
        if not q_tokens:
            q_tokens = tokenize(query[:100])  # fallback minimal
        bm25_scores = self.bm25.get_scores(q_tokens)
        idx_scores = list(enumerate(bm25_scores))
        idx_scores.sort(key=lambda x: x[1], reverse=True)
        return [(int(i), float(s)) for i, s in idx_scores[:top_n]]
