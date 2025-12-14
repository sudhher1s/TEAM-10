# Module 1: Data & Knowledge Base

## Overview
Module 1 is responsible for loading, normalizing, and building a unified knowledge base from multiple medical coding sources (ICD-10, ICD-9→10, CPT, SNOMED).

## Components

### `schemas.py`
Defines standardized data structures:
- **KBItem**: Canonical representation of a medical code
  - `code`: Unique code (e.g., 'I21.9')
  - `title`: Short name/title
  - `description`: Long description
  - `category`: Code category (e.g., 'Cardiovascular')
  - `aliases`: Synonyms and alternate names
  - `metadata`: Extra fields (age restrictions, sex-specific, etc.)
  
- **ICD9to10Mapping**: ICD-9 to ICD-10 mapping
- **KBVersion**: Metadata for KB snapshots
- **LoadStats**: Statistics from loading/processing

### `data_loader.py`
Loads raw medical coding data from files:
- `load_icd10(filepath)` - Load ICD-10 codes from CSV
- `load_icd9to10(filepath)` - Load ICD-9→10 mappings from pipe-delimited TXT
- `load_cpt(filepath)` - Load CPT codes from CSV
- `load_snomed(filepath)` - Load SNOMED CT codes from CSV

### `normalizer.py`
Cleans and standardizes data:
- `normalize_text(text)` - Lowercase, remove extra whitespace
- `expand_abbreviations(text)` - Expand medical abbreviations (SOB → shortness of breath)
- `tokenize(text)` - Split into tokens, optionally remove stopwords
- `generate_aliases(title, description)` - Create synonyms from titles
- `clean_kb_item(item)` - Comprehensive cleaning of a KB item
- `validate_item(item)` - Validate required fields

### `kb_builder.py`
Builds the unified knowledge base:
- `build(...)` - Load, normalize, and merge all sources into unified KB
- `get_item_by_code(code)` - Lookup item by code
- `save_kb_to_json(filepath)` - Persist KB to JSON
- `load_kb_from_json(filepath)` - Load KB from JSON
- `get_kb_version()` - Generate version metadata

## Data Flow

```
ICD10codes.csv
  ↓
DataLoader.load_icd10()
  ↓
DataNormalizer.clean_kb_item()
  ↓
KBBuilder._process_icd10()
  ↓
KBBuilder._deduplicate()
  ↓
Unified KB (List[KBItem])
  ↓
Code-to-Item Index
  ↓
Save to JSON
```

## Usage Example

```python
from pathlib import Path
from src.kb_builder import KBBuilder

workspace_root = Path("c:\\MY PROJECTS\\GEN AI")
data_dir = workspace_root
output_dir = Path("./output")

builder = KBBuilder(data_dir, output_dir)

# Build KB from source files
kb, stats = builder.build(
    icd10_file=data_dir / "ICD10codes.csv",
    icd9to10_file=data_dir / "icd9to10dictionary.txt",
    cpt_file=None,  # Optional
    snomed_file=None  # Optional
)

# Lookup item
item = builder.get_item_by_code("I21.9")
print(f"{item.code}: {item.title}")

# Save KB
builder.save_kb_to_json(output_dir / "kb.json")
```

## Key Features

- **Normalization**: Consistent text processing, abbreviation expansion, alias generation
- **Deduplication**: Remove duplicate codes, keep first occurrence
- **Enrichment**: ICD-9→10 mappings enhance ICD-10 descriptions
- **Validation**: Check required fields before inclusion
- **Versioning**: Track KB changes over time
- **Persistence**: Save/load KB from JSON for reuse

## Testing

Run tests with:
```bash
python test_module1.py
```

Tests cover:
- Text normalization
- Abbreviation expansion
- Alias generation
- KB building from CSV/TXT
- Index lookup
- JSON persistence
- Version metadata

## Data Files Expected

1. **ICD10codes.csv** - CSV with headers:
   ```
   code,title,description,category
   I21.9,Acute myocardial infarction,Heart attack unspecified,Cardiovascular
   ```

2. **icd9to10dictionary.txt** - Pipe-delimited TXT:
   ```
   001.0|A00.0|Cholera
   001.1|A00.0|Cholera vibrios
   ```

3. **cpt.csv** (optional) - CPT codes
4. **snomed.csv** (optional) - SNOMED CT codes
