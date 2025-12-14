"""
Three AI Agents for Medical Coding
1. Retrieval Agent - Finds candidate codes
2. Ranking Agent - Reranks using LLM
3. Classification Agent - Direct prediction
"""
from __future__ import annotations
from typing import Optional, Any
from dataclasses import dataclass
import time


@dataclass
class CodeResult:
    """Result from a coding operation"""
    code: str
    confidence: float
    source: str  # "retrieval", "llm", "classifier", "ensemble"
    explanation: Optional[str] = None
    processing_time: float = 0.0


class RetrievalAgent:
    """
    Agent 1: Semantic Retrieval
    Uses Sentence Transformers to find candidate codes
    """
    
    def __init__(self, semantic_retriever: Any):
        self.retriever = semantic_retriever
        self.agent_name = "RetrievalAgent"
    
    def execute(self, query: str, top_n: int = 50) -> list[CodeResult]:
        """Retrieve candidate codes via semantic search"""
        start = time.time()
        
        results = self.retriever.search(query, top_n=top_n)
        
        codes = [
            CodeResult(
                code=self.retriever.get_code_by_index(idx),
                confidence=score,
                source="retrieval",
                processing_time=time.time() - start
            )
            for idx, score in results
        ]
        
        return codes


class RankingAgent:
    """
    Agent 2: LLM-Powered Ranking
    Uses GPT-4 to intelligently rerank codes
    """
    
    def __init__(self, llm_reranker: Any, icd10_kb: Any):
        self.reranker = llm_reranker
        self.kb = icd10_kb
        self.agent_name = "RankingAgent"
    
    def execute(self, query: str, candidates: list[CodeResult], top_n: int = 5) -> list[CodeResult]:
        """Rerank candidates using LLM"""
        start = time.time()
        
        # Format for LLM
        candidate_dicts = [
            {
                "code": c.code,
                "description": self.kb.get_description(c.code)
            }
            for c in candidates
        ]
        
        # Rerank
        reranked = self.reranker.rerank(query, candidate_dicts, top_n=top_n)
        
        # Convert to CodeResults
        results = [
            CodeResult(
                code=r["code"],
                confidence=r.get("confidence", 0.8),
                source="llm",
                explanation=r.get("reason"),
                processing_time=time.time() - start
            )
            for r in reranked
        ]
        
        return results


class ClassificationAgent:
    """
    Agent 3: Direct ML Prediction
    Uses neural network to directly predict codes
    """
    
    def __init__(self, ml_classifier: Any, semantic_retriever: Any):
        self.classifier = ml_classifier
        self.retriever = semantic_retriever
        self.agent_name = "ClassificationAgent"
    
    def execute(self, query: str, top_n: int = 10) -> list[CodeResult]:
        """Directly predict codes using ML classifier"""
        start = time.time()
        
        # Get embedding
        import numpy as np
        embedding = self.retriever.model.encode([query])[0]
        embedding = np.array([embedding])
        
        # Predict
        predictions = self.classifier.predict(embedding, threshold=0.3)
        
        results = [
            CodeResult(
                code=code,
                confidence=conf,
                source="classifier",
                processing_time=time.time() - start
            )
            for code, conf in predictions[0][:top_n]
        ]
        
        return results


class EnsembleCoordinator:
    """
    Coordinates all three agents
    Implements RAG pipeline with consensus voting
    """
    
    def __init__(self, retrieval: RetrievalAgent, ranking: RankingAgent, 
                 classification: ClassificationAgent):
        self.retrieval = retrieval
        self.ranking = ranking
        self.classification = classification
        print("✓ Ensemble Coordinator initialized with 3 AI agents")
    
    def predict(self, query: str, method: str = "ensemble") -> list[CodeResult]:
        """
        Predict codes using selected method
        
        Methods:
        - "retrieval": Fast semantic search only
        - "llm": Retrieval + LLM reranking (best quality)
        - "classifier": Direct ML prediction (fastest)
        - "ensemble": All 3 with voting (recommended)
        """
        
        if method == "retrieval":
            return self._retrieval_pipeline(query)
        elif method == "llm":
            return self._rag_pipeline(query)
        elif method == "classifier":
            return self._classifier_pipeline(query)
        else:  # ensemble
            return self._ensemble_pipeline(query)
    
    def _retrieval_pipeline(self, query: str) -> list[CodeResult]:
        """Fast retrieval-only pipeline"""
        results = self.retrieval.execute(query, top_n=10)
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:10]
    
    def _rag_pipeline(self, query: str) -> list[CodeResult]:
        """RAG: Retrieval + LLM Reranking (BEST QUALITY)"""
        # Step 1: Retrieve candidates
        candidates = self.retrieval.execute(query, top_n=50)
        
        # Step 2: Rerank with LLM
        reranked = self.ranking.execute(query, candidates, top_n=10)
        
        return reranked
    
    def _classifier_pipeline(self, query: str) -> list[CodeResult]:
        """Fast direct prediction"""
        results = self.classification.execute(query, top_n=10)
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:10]
    
    def _ensemble_pipeline(self, query: str) -> list[CodeResult]:
        """Ensemble: Combine all 3 agents with voting"""
        # Run all three agents
        retrieval_results = self.retrieval.execute(query, top_n=20)
        classifier_results = self.classification.execute(query, top_n=20)
        
        # Rerank top retrieval results
        ranking_results = self.ranking.execute(query, retrieval_results[:20], top_n=10)
        
        # Ensemble voting
        votes = {}
        
        # Weight by source and confidence
        for result in ranking_results:
            votes[result.code] = votes.get(result.code, 0) + result.confidence * 0.5
        
        for result in classifier_results:
            votes[result.code] = votes.get(result.code, 0) + result.confidence * 0.3
        
        for result in retrieval_results[:10]:
            votes[result.code] = votes.get(result.code, 0) + result.confidence * 0.2
        
        # Create ensemble results
        ensemble_results = [
            CodeResult(
                code=code,
                confidence=min(score, 1.0),
                source="ensemble"
            )
            for code, score in sorted(votes.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return ensemble_results[:10]
