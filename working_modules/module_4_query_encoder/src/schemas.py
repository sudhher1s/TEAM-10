from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class QueryResultItem:
    code: str
    title: str
    category: Optional[str]
    score: float
    index_id: int

@dataclass
class QueryResults:
    query: str
    top_k: int
    items: List[QueryResultItem]
    elapsed_ms: float

@dataclass
class EncoderMetadata:
    model_name: str
    embedding_dim: int
    normalized: bool

