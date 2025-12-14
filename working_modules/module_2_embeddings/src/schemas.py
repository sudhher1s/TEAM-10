"""
Module 2: Embeddings Builder - Data Schemas
Defines dataclasses for embeddings metadata and versioning.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import json


@dataclass
class EmbeddingItem:
    """Represents a single embedded KB item."""
    embeddings_id: int  # Index in embeddings matrix
    code: str
    title: str
    description: str
    category: str
    embedding_dim: int  # Dimensionality of embedding (e.g., 384)


@dataclass
class EmbeddingsMetadata:
    """Metadata for embeddings collection."""
    model_name: str  # e.g., "all-MiniLM-L6-v2"
    embedding_dim: int  # e.g., 384
    num_embeddings: int
    num_kb_items: int
    timestamp: str  # ISO format timestamp
    kb_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbeddingsMetadata':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class EmbeddingsStats:
    """Statistics about embedding process."""
    total_items: int
    embedded_items: int
    failed_items: int
    embedding_time_seconds: float
    avg_time_per_item_ms: float
    embedding_dim: int
    model_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ItemMetadata:
    """Metadata for a single item in the embeddings collection."""
    embeddings_id: int
    code: str
    title: str
    description: str
    category: str
    embedding_dim: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemMetadata':
        """Create from dictionary."""
        return cls(**data)
