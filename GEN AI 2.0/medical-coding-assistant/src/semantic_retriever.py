"""
Semantic Retriever using Sentence Transformers
Replaces BM25 with neural semantic search
"""
from __future__ import annotations
from typing import List, Tuple
from sentence_transformers import SentenceTransformer, util
import numpy as np


class SemanticRetriever:
    """
    Neural semantic search using Sentence Transformers
    Supports medical domain and general embeddings
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic retriever with pre-trained model
        
        Models:
        - all-MiniLM-L6-v2: Fast, general purpose (384 dims)
        - all-mpnet-base-v2: Better quality, slower (768 dims)
        - allenai-specter: Medical domain (768 dims)
        """
        print(f"Loading semantic model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.docs = []
        self.codes = []
        self.embeddings = None
        print(f"✓ Model loaded with embedding dim: {self.model.get_sentence_embedding_dimension()}")

    def fit(self, kb: list[dict]) -> None:
        """
        Encode all ICD-10 codes in knowledge base
        Done once at startup for efficiency
        """
        print(f"Encoding {len(kb)} medical codes...")
        
        self.docs = [
            (str(item.get("title", "")) + " " + str(item.get("description", ""))).strip()
            for item in kb
        ]
        self.codes = [str(item.get("icd10_code", "")) for item in kb]
        
        # Encode all documents
        self.embeddings = self.model.encode(self.docs, convert_to_tensor=True, show_progress_bar=True)
        print(f"✓ Encoded {len(self.docs)} documents")

    def search(self, query: str, top_n: int = 50) -> List[Tuple[int, float]]:
        """
        Semantic search - find most similar codes
        
        Returns: [(index, similarity_score), ...]
        """
        if self.embeddings is None:
            raise RuntimeError("Retriever not fitted")
        
        # Encode query
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Compute similarities
        similarities = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
        
        # Get top results
        top_results = np.argsort(similarities.cpu().numpy())[-top_n:][::-1]
        
        results = [
            (int(idx), float(similarities[idx].cpu().numpy()))
            for idx in top_results
        ]
        
        return results

    def get_code_by_index(self, idx: int) -> str:
        """Get ICD-10 code by index"""
        return self.codes[idx] if idx < len(self.codes) else ""

    def get_doc_by_index(self, idx: int) -> str:
        """Get document text by index"""
        return self.docs[idx] if idx < len(self.docs) else ""
