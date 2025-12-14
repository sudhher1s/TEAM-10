"""
Demo: Data Normalization in Module 1
Shows BEFORE and AFTER examples
"""
import sys
sys.path.insert(0, 'src')

from normalizer import DataNormalizer

print("\n" + "=" * 80)
print("DATA NORMALIZATION EXAMPLES - MODULE 1")
print("=" * 80)

# Example 1: Basic normalization (whitespace, case, punctuation)
print("\n[EXAMPLE 1] Whitespace, Case, Punctuation Cleanup")
print("-" * 80)

raw_1 = {
    'code': '  i2101  ',
    'title': '  ACUTE MYOCARDIAL INFARCTION OF ANTERIOR WALL  ',
    'description': '  Acute MI with S-T elevation; initial encounter.  ',
    'category': '  CARDIAC  '
}

print("BEFORE (raw CSV data):")
for k, v in raw_1.items():
    print(f"  {k}: '{v}'")

cleaned_1 = DataNormalizer.clean_kb_item(raw_1)

print("\nAFTER (normalized):")
for k, v in cleaned_1.items():
    if k != 'aliases':
        print(f"  {k}: {v}")

# Example 2: Abbreviation expansion
print("\n\n[EXAMPLE 2] Abbreviation Expansion")
print("-" * 80)

raw_2 = {
    'code': 'I25.1',
    'title': 'Patient with CHF and DM',
    'description': 'Congestive heart failure; r/o MI; SOB present; dx: HTN',
    'category': 'cardiac'
}

print("BEFORE (raw):")
print(f"  title: {raw_2['title']}")
print(f"  description: {raw_2['description']}")

cleaned_2 = DataNormalizer.clean_kb_item(raw_2)

print("\nAFTER (abbreviations expanded):")
print(f"  title: {cleaned_2['title']}")
print(f"  description: {cleaned_2['description']}")

# Example 3: Alias generation
print("\n\n[EXAMPLE 3] Alias Generation")
print("-" * 80)

raw_3 = {
    'code': 'I21.01',
    'title': 'acute myocardial infarction',
    'description': 'MI of anterior wall, STEMI',
    'category': 'cardiac'
}

print(f"BEFORE:")
print(f"  title: {raw_3['title']}")
print(f"  description: {raw_3['description']}")

cleaned_3 = DataNormalizer.clean_kb_item(raw_3)

print(f"\nAFTER (aliases generated):")
print(f"  aliases: {cleaned_3['aliases']}")

# Example 4: Real-world messy data
print("\n\n[EXAMPLE 4] Real-World Messy Data")
print("-" * 80)

messy = {
    'code': '  J45.9  ',
    'title': '   ASTHMA -- Unspecified   ',
    'description': '  Asthma, unspecified type; r/o URI; DM comorbidity  ',
    'category': '  RESPIRATORY DISEASE  '
}

print("BEFORE (messy):")
import json
print(json.dumps(messy, indent=2))

cleaned_messy = DataNormalizer.clean_kb_item(messy)

print("\nAFTER (clean & ready for ML):")
print(json.dumps({k: v for k, v in cleaned_messy.items() if k != 'metadata'}, indent=2))

print("\n" + "=" * 80)
print("WHY NORMALIZATION MATTERS FOR MODULE 2 (EMBEDDINGS)")
print("=" * 80)
print("""
1. CONSISTENCY: All titles are lowercase, no extra spaces
   → SentenceTransformer processes uniform input

2. SEMANTIC CLARITY: "CHF" → "congestive heart failure"
   → Model understands the full clinical meaning

3. ALIASES: "heart attack", "MI", "AMI" all point to same concept
   → Better semantic similarity matching

4. QUALITY CONTROL: Invalid codes, missing titles are caught
   → 71,704 clean items enter the embedding pipeline

Without normalization:
  - "Heart Attack" vs "HEART ATTACK" vs "heart attack" = 3 different texts
  - "MI" and "Myocardial Infarction" not recognized as related
  - Embeddings would be scattered in vector space

With normalization:
  - Single canonical form
  - Abbreviations expanded to full meaning
  - Embeddings cluster correctly by medical concept
""")
