"""
Module 1: Data Loader
Loads ICD-10, ICD-9→10, CPT, SNOMED from CSV/TXT files.
"""
from __future__ import annotations
import csv
import os
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load medical coding datasets from CSV/TXT files."""
    
    def __init__(self, data_dir: Path):
        """
        Args:
            data_dir: Path to directory containing raw data files.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_icd10(self, filepath: Path) -> List[Dict[str, str]]:
        """
        Load ICD-10 codes from CSV.
        Expected format (no header): chapter,sub,code,full_desc,alt_desc,category
        Example: A00,0,A000,"Cholera...","Cholera...","Cholera"
        """
        rows = []
        if not filepath.exists():
            logger.warning(f"ICD-10 file not found: {filepath}")
            return rows
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 6:
                        continue
                    code = row[2].strip()  # code is 3rd column (0-indexed)
                    if not code:
                        continue
                    rows.append({
                        'code': code,
                        'title': row[3].strip() or row[4].strip(),  # full_desc or alt_desc
                        'description': row[3].strip(),  # full_desc
                        'category': row[5].strip() if len(row) > 5 else '',  # category
                        'code_system': 'ICD-10'
                    })
            logger.info(f"Loaded {len(rows)} ICD-10 records from {filepath}")
        except Exception as e:
            logger.error(f"Error loading ICD-10: {e}")
        
        return rows
    
    def load_icd9to10(self, filepath: Path) -> List[Dict[str, str]]:
        """
        Load ICD-9 to ICD-10 mappings from pipe-delimited TXT.
        Expected format: icd9_code|icd10_code|description
        """
        mappings = []
        if not filepath.exists():
            logger.warning(f"ICD9→10 mapping file not found: {filepath}")
            return mappings
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('|')
                    if len(parts) < 3:
                        continue
                    mappings.append({
                        'icd9_code': parts[0].strip(),
                        'icd10_code': parts[1].strip(),
                        'description': parts[2].strip()
                    })
            logger.info(f"Loaded {len(mappings)} ICD-9→10 mappings from {filepath}")
        except Exception as e:
            logger.error(f"Error loading ICD9→10 mappings: {e}")
        
        return mappings
    
    def load_cpt(self, filepath: Path) -> List[Dict[str, str]]:
        """Load CPT codes from CSV."""
        rows = []
        if not filepath.exists():
            logger.warning(f"CPT file not found: {filepath}")
            return rows
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row.get('code', '').strip():
                        continue
                    rows.append({
                        'code': row.get('code', '').strip(),
                        'title': row.get('title', ''),
                        'description': row.get('description', ''),
                        'category': row.get('category', ''),
                        'code_system': 'CPT'
                    })
            logger.info(f"Loaded {len(rows)} CPT records from {filepath}")
        except Exception as e:
            logger.error(f"Error loading CPT: {e}")
        
        return rows
    
    def load_snomed(self, filepath: Path) -> List[Dict[str, str]]:
        """Load SNOMED CT codes from CSV."""
        rows = []
        if not filepath.exists():
            logger.warning(f"SNOMED file not found: {filepath}")
            return rows
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row.get('code', '').strip():
                        continue
                    rows.append({
                        'code': row.get('code', '').strip(),
                        'title': row.get('title', ''),
                        'description': row.get('description', ''),
                        'category': row.get('category', ''),
                        'code_system': 'SNOMED'
                    })
            logger.info(f"Loaded {len(rows)} SNOMED records from {filepath}")
        except Exception as e:
            logger.error(f"Error loading SNOMED: {e}")
        
        return rows
