from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Evidence:
    """Rich evidence context for a single code."""
    code: str
    title: str
    description: Optional[str]
    category: Optional[str]
    aliases: List[str]
    relevance_score: float

@dataclass
class EvidenceSet:
    """Evidence for a list of reranked results."""
    query: str
    items: List[Evidence]
    elapsed_ms: float
