"""
Module 3: Vector Index - Data Schemas
Defines structures for FAISS index metadata and search results.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json


@dataclass
class SearchResult:
    """Represents a single search result from vector similarity search."""
    code: str
    title: str
    category: str
    description: str
    similarity_score: float  # 0.0 to 1.0
    embeddings_id: int


@dataclass
class SearchResults:
    """Batch of search results."""
    query: str
    top_k: int
    results: List[SearchResult]
    search_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'query': self.query,
            'top_k': self.top_k,
            'results': [asdict(r) for r in self.results],
            'search_time_ms': self.search_time_ms,
            'timestamp': self.timestamp
        }


@dataclass
class IndexMetadata:
    """Metadata for FAISS index."""
    index_type: str  # 'IVF', 'HNSW', 'FLAT', etc.
    embedding_dim: int
    num_vectors: int
    num_probes: int  # For IVF (accuracy/speed tradeoff)
    nlist: int  # Number of clusters for IVF
    metric: str  # 'L2', 'IP' (inner product)
    model_name: str
    kb_version: str
    timestamp: str
    embeddings_path: str
    metadata_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndexMetadata':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class IndexStats:
    """Statistics about index building process."""
    num_vectors: int
    embedding_dim: int
    index_type: str
    build_time_seconds: float
    index_size_bytes: int
    index_size_mb: float
    vectors_per_second: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
