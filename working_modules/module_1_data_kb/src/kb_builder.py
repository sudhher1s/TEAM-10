"""
Module 1: Knowledge Base Builder
Merges ICD-10, ICD-9→10, CPT, SNOMED into a unified, deduplicated KB.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
import json
import logging

from .schemas import KBItem, KBVersion, LoadStats
from .data_loader import DataLoader
from .normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class KBBuilder:
    """Build and manage a unified knowledge base."""
    
    def __init__(self, data_dir: Path, output_dir: Path):
        """
        Args:
            data_dir: Input data directory (contains CSV/TXT files).
            output_dir: Output directory for KB artifacts.
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = DataLoader(self.data_dir)
        self.normalizer = DataNormalizer()
        self.kb: List[KBItem] = []
        self.code_to_item: Dict[str, KBItem] = {}
    
    def build(
        self,
        icd10_file: Path,
        icd9to10_file: Path,
        cpt_file: Path | None = None,
        snomed_file: Path | None = None
    ) -> Tuple[List[KBItem], LoadStats]:
        """
        Build unified KB from source files.
        
        Returns:
            (kb_items, stats)
        """
        stats = LoadStats(
            raw_rows_loaded=0,
            rows_after_cleaning=0,
            rows_after_dedup=0,
            total_items=0,
            duplicates_removed=0
        )
        
        # Load ICD-10
        logger.info("Loading ICD-10 codes...")
        icd10_rows = self.loader.load_icd10(icd10_file)
        stats.raw_rows_loaded += len(icd10_rows)
        
        # Load ICD-9→10 mappings
        logger.info("Loading ICD-9→10 mappings...")
        icd9to10_rows = self.loader.load_icd9to10(icd9to10_file)
        logger.info(f"Loaded {len(icd9to10_rows)} ICD-9→10 mappings")
        
        # Load optional CPT and SNOMED
        cpt_rows = []
        snomed_rows = []
        if cpt_file:
            logger.info("Loading CPT codes...")
            cpt_rows = self.loader.load_cpt(cpt_file)
            stats.raw_rows_loaded += len(cpt_rows)
        
        if snomed_file:
            logger.info("Loading SNOMED codes...")
            snomed_rows = self.loader.load_snomed(snomed_file)
            stats.raw_rows_loaded += len(snomed_rows)
        
        # Merge ICD-10 with ICD-9→10 descriptions (enrich)
        icd10_items = self._process_icd10(icd10_rows, icd9to10_rows)
        stats.rows_after_cleaning = len(icd10_items)
        
        # Deduplicate by code
        all_items = icd10_items + self._process_other(cpt_rows) + self._process_other(snomed_rows)
        deduplicated, dups_removed = self._deduplicate(all_items)
        stats.rows_after_dedup = len(deduplicated)
        stats.duplicates_removed = dups_removed
        stats.total_items = len(deduplicated)
        
        self.kb = deduplicated
        self._build_index()
        
        logger.info(f"KB built: {stats.total_items} unique items")
        logger.info(stats.summary())
        
        return self.kb, stats
    
    def _process_icd10(
        self,
        icd10_rows: List[Dict],
        icd9to10_rows: List[Dict]
    ) -> List[KBItem]:
        """
        Process ICD-10 rows and enrich with ICD-9→10 mappings.
        """
        items = []
        
        # Build ICD-9→10 mapping for lookup
        icd10_to_desc = {}
        for mapping in icd9to10_rows:
            icd10_code = mapping.get('icd10_code', '').strip()
            desc = mapping.get('description', '').strip()
            if icd10_code and desc:
                # Keep the longest description for each code
                if icd10_code not in icd10_to_desc or len(desc) > len(icd10_to_desc[icd10_code]):
                    icd10_to_desc[icd10_code] = desc
        
        # Process ICD-10 rows
        for row in icd10_rows:
            is_valid, error = self.normalizer.validate_item(row)
            if not is_valid:
                logger.debug(f"Skipping invalid ICD-10 row: {error}")
                continue
            
            cleaned = self.normalizer.clean_kb_item(row)
            code = cleaned['code']
            
            # Enrich description with ICD-9→10 mapping if available
            if code in icd10_to_desc and not cleaned['description']:
                cleaned['description'] = icd10_to_desc[code]
            
            item = KBItem(
                code=code,
                title=cleaned['title'],
                description=cleaned['description'],
                category=cleaned['category'],
                code_system='ICD-10',
                aliases=cleaned.get('aliases', [])
            )
            items.append(item)
        
        return items
    
    def _process_other(self, rows: List[Dict]) -> List[KBItem]:
        """Process CPT, SNOMED, or other rows."""
        items = []
        for row in rows:
            is_valid, error = self.normalizer.validate_item(row)
            if not is_valid:
                logger.debug(f"Skipping invalid row: {error}")
                continue
            
            cleaned = self.normalizer.clean_kb_item(row)
            item = KBItem(
                code=cleaned['code'],
                title=cleaned['title'],
                description=cleaned['description'],
                category=cleaned['category'],
                code_system=cleaned.get('code_system', 'OTHER'),
                aliases=cleaned.get('aliases', [])
            )
            items.append(item)
        
        return items
    
    def _deduplicate(self, items: List[KBItem]) -> Tuple[List[KBItem], int]:
        """
        Deduplicate items by code. Keep first occurrence.
        
        Returns:
            (deduplicated_items, num_duplicates_removed)
        """
        seen_codes: Set[str] = set()
        deduplicated = []
        duplicates = 0
        
        for item in items:
            if item.code not in seen_codes:
                deduplicated.append(item)
                seen_codes.add(item.code)
            else:
                duplicates += 1
                logger.debug(f"Duplicate removed: {item.code}")
        
        return deduplicated, duplicates
    
    def _build_index(self) -> None:
        """Build in-memory code-to-item index."""
        self.code_to_item = {item.code: item for item in self.kb}
    
    def get_item_by_code(self, code: str) -> KBItem | None:
        """Lookup item by code."""
        return self.code_to_item.get(code.upper())
    
    def save_kb_to_json(self, filepath: Path) -> None:
        """Save KB to JSON."""
        data = [item.to_dict() for item in self.kb]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved KB to {filepath} ({len(self.kb)} items)")
    
    def load_kb_from_json(self, filepath: Path) -> None:
        """Load KB from JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.kb = []
        for item_dict in data:
            item = KBItem(**item_dict)
            self.kb.append(item)
        
        self._build_index()
        logger.info(f"Loaded KB from {filepath} ({len(self.kb)} items)")
    
    def get_kb_version(self) -> KBVersion:
        """Generate version metadata for current KB."""
        icd10_count = sum(1 for item in self.kb if item.code_system == 'ICD-10')
        cpt_count = sum(1 for item in self.kb if item.code_system == 'CPT')
        snomed_count = sum(1 for item in self.kb if item.code_system == 'SNOMED')
        
        return KBVersion(
            version_id=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            icd10_count=icd10_count,
            cpt_count=cpt_count,
            snomed_count=snomed_count,
            total_items=len(self.kb),
            source_files={}
        )
