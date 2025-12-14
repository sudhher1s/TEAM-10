"""
Module 4: Query Encoder
Encodes user queries using the same sentence-transformers model as Module 2
and searches the FAISS index built in Module 3.
"""
import json
import time
from pathlib import Path
from typing import List, Optional

import numpy as np
from dataclasses import asdict
from .schemas import QueryResultItem, QueryResults, EncoderMetadata

try:
    import faiss
except ImportError:
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

class QueryEncoder:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize: bool = True,
        index_path: Optional[Path] = None,
        item_metadata_path: Optional[Path] = None,
    ):
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers not installed. pip install sentence-transformers")
        if faiss is None:
            raise ImportError("faiss not installed. pip install faiss-cpu")
        self.model_name = model_name
        self.normalize = normalize
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.item_metadata = None
        if index_path:
            self.load_index(index_path)
        if item_metadata_path:
            with open(item_metadata_path, "r", encoding="utf-8") as f:
                self.item_metadata = json.load(f)

    def encode(self, texts: List[str]) -> np.ndarray:
        vectors = self.model.encode(texts, batch_size=1, show_progress_bar=False)
        vecs = np.asarray(vectors, dtype=np.float32)
        if self.normalize:
            faiss.normalize_L2(vecs)
        return vecs

    def load_index(self, index_path: Path):
        self.index = faiss.read_index(str(index_path))

    def search(self, query: str, top_k: int = 10) -> QueryResults:
        if self.index is None:
            raise RuntimeError("FAISS index not loaded. Provide index_path in constructor or call load_index().")
        if self.item_metadata is None:
            raise RuntimeError("Item metadata not loaded. Provide item_metadata_path in constructor.")

        t0 = time.time()
        qvec = self.encode([query])
        distances, indices = self.index.search(qvec, top_k)
        # Convert FAISS L2 distances to similarity (1 / (1 + d)) for readability
        sims = 1.0 / (1.0 + distances[0])
        items: List[QueryResultItem] = []
        for rank, (idx, score) in enumerate(zip(indices[0], sims)):
            if idx < 0:
                continue
            meta = self.item_metadata[idx]
            items.append(QueryResultItem(
                code=meta.get("code"),
                title=meta.get("title"),
                category=meta.get("category"),
                score=float(score),
                index_id=int(idx),
            ))
        elapsed_ms = (time.time() - t0) * 1000.0
        return QueryResults(query=query, top_k=top_k, items=items, elapsed_ms=elapsed_ms)

    def save_metadata(self, output_path: Path):
        meta = EncoderMetadata(
            model_name=self.model_name,
            embedding_dim=self.model.get_sentence_embedding_dimension(),
            normalized=self.normalize,
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(meta), f, indent=2)

