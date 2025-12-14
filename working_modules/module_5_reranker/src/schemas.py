from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RerankedItem:
    code: str
    title: str
    category: Optional[str]
    score: float  # cross-encoder relevance score
    index_id: int

@dataclass
class RerankResults:
    query: str
    items: List[RerankedItem]
    elapsed_ms: float
