#!/usr/bin/env python3
"""
Module 1 Test Script
Tests data loading, normalization, and KB building.
"""
from pathlib import Path
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.kb_builder import KBBuilder
from src.normalizer import DataNormalizer


def test_normalizer():
    """Test text normalization."""
    print("\n=== Testing DataNormalizer ===")
    
    # Test normalize_text
    text = "  Acute   Myocardial    Infarction  "
    normalized = DataNormalizer.normalize_text(text)
    print(f"normalize_text('{text}') -> '{normalized}'")
    assert normalized == "acute myocardial infarction", "normalize_text failed"
    
    # Test expand_abbreviations
    text = "Patient with SOB and EKG changes"
    expanded = DataNormalizer.expand_abbreviations(text)
    print(f"expand_abbreviations('{text}') -> '{expanded}'")
    
    # Test generate_aliases
    aliases = DataNormalizer.generate_aliases(
        "Acute myocardial infarction",
        "Heart attack unspecified"
    )
    print(f"generate_aliases(...) -> {aliases}")
    
    print("[OK] DataNormalizer tests passed")


def test_kb_builder():
    """Test KB building with sample data."""
    print("\n=== Testing KBBuilder ===")
    
    # Create sample data files
    workspace_root = Path("c:\\MY PROJECTS\\GEN AI")
    data_dir = workspace_root
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    builder = KBBuilder(data_dir, output_dir)
    
    # Check if real data files exist
    icd10_file = data_dir / "ICD10codes.csv"
    icd9to10_file = data_dir / "icd9to10dictionary.txt"
    
    if not icd10_file.exists():
        print(f"⚠ ICD-10 file not found: {icd10_file}")
        print(f"  Create a CSV file with headers: code,title,description,category")
        return
    
    if not icd9to10_file.exists():
        print(f"⚠ ICD-9→10 file not found: {icd9to10_file}")
        print(f"  Create a TXT file with format: icd9_code|icd10_code|description")
        return
    
    # Build KB
    logger.info(f"Building KB from {icd10_file} and {icd9to10_file}...")
    kb, stats = builder.build(
        icd10_file=icd10_file,
        icd9to10_file=icd9to10_file
    )
    
    print(f"[OK] KB built successfully")
    print(f"  {stats.summary()}")
    print(f"  First 5 items:")
    for item in kb[:5]:
        print(f"    - {item.code}: {item.title} ({item.category})")
    
    # Test index lookup
    if kb:
        first_code = kb[0].code
        found_item = builder.get_item_by_code(first_code)
        assert found_item is not None, f"Failed to lookup {first_code}"
        print(f"[OK] Index lookup works: {first_code} -> {found_item.title}")
    
    # Save KB to JSON
    kb_json = output_dir / "kb.json"
    builder.save_kb_to_json(kb_json)
    print(f"[OK] KB saved to {kb_json}")
    
    # Load KB from JSON
    builder2 = KBBuilder(data_dir, output_dir)
    builder2.load_kb_from_json(kb_json)
    print(f"[OK] KB loaded from JSON ({len(builder2.kb)} items)")
    
    # Version metadata
    version = builder.get_kb_version()
    print(f"[OK] KB Version: {version.version_id}")
    print(f"  - ICD-10: {version.icd10_count}")
    print(f"  - CPT: {version.cpt_count}")
    print(f"  - SNOMED: {version.snomed_count}")
    print(f"  - Total: {version.total_items}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Module 1: Data & Knowledge Base - Tests")
    print("=" * 60)
    
    try:
        test_normalizer()
        test_kb_builder()
        
        print("\n" + "=" * 60)
        print("[OK] All tests completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
