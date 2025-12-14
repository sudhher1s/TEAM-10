"""
Module 1: Data Normalizer
Cleans, normalizes, and standardizes KB items (lowercasing, punctuation, spelling).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Set
import logging

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Clean and normalize medical coding data."""
    
    # Common medical abbreviations to expand
    ABBREVIATIONS = {
        'SOB': 'shortness of breath',
        'EKG': 'electrocardiogram',
        'ECG': 'electrocardiogram',
        'CHF': 'congestive heart failure',
        'MI': 'myocardial infarction',
        'CVA': 'cerebrovascular accident',
        'HTN': 'hypertension',
        'DM': 'diabetes mellitus',
        'COPD': 'chronic obstructive pulmonary disease',
        'URI': 'upper respiratory infection',
        'UTI': 'urinary tract infection',
        'r/o': 'rule out',
        'dx': 'diagnosis',
        'tx': 'treatment',
        'rx': 'treatment'
    }
    
    # Common stopwords to filter
    STOPWORDS = {
        'a', 'an', 'the', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'been',
        'of', 'for', 'with', 'to', 'in', 'on', 'at', 'by', 'as', 'from',
        'this', 'that', 'these', 'those', 'not', 'no', 'yes', 'other',
        'unspecified', 'unilateral', 'bilateral'
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text: lowercase, remove extra whitespace, standardize punctuation.
        """
        if not text:
            return ''
        
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Standardize punctuation (remove trailing periods, commas)
        text = re.sub(r'[,;:]+$', '', text)
        
        return text
    
    @staticmethod
    def expand_abbreviations(text: str) -> str:
        """Expand common medical abbreviations."""
        for abbr, expansion in DataNormalizer.ABBREVIATIONS.items():
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def remove_punctuation(text: str) -> str:
        """Remove non-alphanumeric except spaces and hyphens."""
        text = re.sub(r'[^\w\s\-\.]', '', text)
        return text
    
    @staticmethod
    def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
        """
        Tokenize text into words; optionally remove stopwords.
        """
        tokens = text.lower().split()
        if remove_stopwords:
            tokens = [t for t in tokens if t not in DataNormalizer.STOPWORDS and len(t) > 1]
        return tokens
    
    @staticmethod
    def generate_aliases(title: str, description: str) -> List[str]:
        """
        Generate common aliases from title and description.
        E.g., "Acute myocardial infarction" → ["acute MI", "heart attack"]
        """
        aliases = []
        
        # Extract first few words as alias
        title_words = title.split()
        if len(title_words) > 2:
            aliases.append(' '.join(title_words[:2]))
        
        # Common healthcare aliases (manual list; can be extended)
        title_lower = title.lower()
        if 'myocardial infarction' in title_lower or 'heart attack' in title_lower:
            aliases.extend(['MI', 'heart attack', 'AMI'])
        if 'hypertension' in title_lower:
            aliases.extend(['high blood pressure', 'HTN'])
        if 'diabetes' in title_lower:
            aliases.extend(['DM', 'blood sugar'])
        if 'pneumonia' in title_lower:
            aliases.append('lung infection')
        if 'stroke' in title_lower or 'cva' in title_lower:
            aliases.extend(['CVA', 'brain attack'])
        
        # Deduplicate and normalize
        aliases = list(set([DataNormalizer.normalize_text(a) for a in aliases if a]))
        return aliases
    
    @staticmethod
    def clean_kb_item(item: dict) -> dict:
        """
        Clean a single KB item: normalize fields, expand abbr, generate aliases.
        """
        cleaned = item.copy()
        cleaned['code'] = cleaned.get('code', '').strip().upper()
        cleaned['title'] = DataNormalizer.normalize_text(cleaned.get('title', ''))
        cleaned['description'] = DataNormalizer.normalize_text(cleaned.get('description', ''))
        cleaned['category'] = DataNormalizer.normalize_text(cleaned.get('category', ''))
        
        # Expand abbreviations in title and description
        cleaned['title'] = DataNormalizer.expand_abbreviations(cleaned['title'])
        cleaned['description'] = DataNormalizer.expand_abbreviations(cleaned['description'])
        
        # Generate aliases
        if 'aliases' not in cleaned or not cleaned['aliases']:
            cleaned['aliases'] = DataNormalizer.generate_aliases(
                cleaned['title'], cleaned['description']
            )
        
        return cleaned
    
    @staticmethod
    def validate_item(item: dict) -> Tuple[bool, str]:
        """
        Validate a KB item. Return (is_valid, error_msg).
        """
        if not item.get('code', '').strip():
            return False, "Missing code"
        if not item.get('title', '').strip():
            return False, f"Missing title for {item.get('code')}"
        if len(item.get('code', '')) > 20:
            return False, f"Code too long: {item.get('code')}"
        return True, ""
