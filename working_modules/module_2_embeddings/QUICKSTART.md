# Module 2: Embeddings Builder

This module generates semantic embeddings for medical codes using sentence-transformers.

## Quick Start

```bash
# Install dependencies
pip install sentence-transformers torch numpy

# Run tests
python test_module2.py
```

## Files

- `src/schemas.py` - Data structures (EmbeddingItem, EmbeddingsMetadata, EmbeddingsStats)
- `src/embeddings_builder.py` - Core EmbeddingsBuilder class
- `test_module2.py` - Test suite
- `README.md` - Full documentation
- `output/` - Generated embeddings and metadata

## Output

When you run `python test_module2.py`, it will:

1. Load KB from Module 1 (`module_1_data_kb/output/kb.json`)
2. Initialize sentence-transformers with `all-MiniLM-L6-v2`
3. Generate 384-dimensional embeddings for each KB item
4. Save to `output/`:
   - `embeddings.npy` - (71704 x 384) embedding matrix
   - `item_metadata.json` - Code, title, category for each embedding
   - `code_to_index.json` - Mapping from code to embedding row
   - `metadata.json` - Model and dataset info
   - `stats.json` - Timing and statistics

## Integration

Module 2 output feeds into:
- **Module 3 (Vector Index)**: Uses embeddings to build FAISS index
- **Module 4 (Query Encoder)**: Uses same model to encode queries
- **Module 5 (Reranker)**: Uses metadata to re-score results
