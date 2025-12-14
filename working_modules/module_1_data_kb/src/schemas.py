"""
Module 1: Data & Knowledge Base - Schema Definitions
Defines standardized data structures for KB items, ICD mappings, and KB versions.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class KBItem:
    """Canonical KB item representing a single medical code (ICD-10, CPT, SNOMED)."""
    code: str  # Unique code (e.g., 'I21.9', 'J45.901')
    title: str  # Short title/name
    description: str  # Long description
    category: str  # Category (e.g., 'Cardiovascular', 'Respiratory')
    code_system: str = "ICD-10"  # Code system type (ICD-10, CPT, SNOMED, etc.)
    aliases: List[str] = None  # Synonyms or alternate names
    parent_code: Optional[str] = None  # Parent code for hierarchies
    metadata: Dict[str, Any] = None  # Extra fields (age restrictions, sex-specific, etc.)
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        return d
    
    def searchable_text(self) -> str:
        """Concatenate all searchable fields for IR."""
        parts = [self.title, self.description] + self.aliases
        return " ".join(filter(None, parts))


@dataclass
class ICD9to10Mapping:
    """ICD-9 to ICD-10 mapping."""
    icd9_code: str
    icd10_code: str
    description: str
    confidence: float = 1.0  # Mapping confidence (0-1)


@dataclass
class KBVersion:
    """Metadata for a KB snapshot."""
    version_id: str
    timestamp: datetime
    icd10_count: int
    cpt_count: int
    snomed_count: int
    total_items: int
    source_files: Dict[str, str]  # {filename: md5_hash}
    notes: str = ""


@dataclass
class LoadStats:
    """Statistics from loading/processing."""
    raw_rows_loaded: int
    rows_after_cleaning: int
    rows_after_dedup: int
    total_items: int
    duplicates_removed: int
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            f"Loaded {self.raw_rows_loaded} rows → "
            f"{self.rows_after_cleaning} after cleaning → "
            f"{self.rows_after_dedup} after dedup → "
            f"{self.total_items} final items. "
            f"Removed {self.duplicates_removed} duplicates. "
            f"Errors: {len(self.errors)}"
        )
