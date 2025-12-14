# Module 2: Embeddings Builder

## Purpose

Generate semantic embeddings (384-dimensional vectors) for all medical codes in the knowledge base using a pre-trained bi-encoder model. This module transforms text-based KB items into numerical vectors suitable for similarity-based retrieval.

## Overview

```
Module 1 (KB)
    ↓
    kb.json (71,704 items)
    ↓
[Module 2 - Embeddings Builder]
    ↓
    embeddings.npy (71,704 x 384 matrix)
    item_metadata.json (code, title, category)
    code_to_index.json (code → row mapping)
    ↓
Module 3 (Vector Index)
```

## Key Features

- **Bi-Encoder Model**: Uses `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
- **Batch Processing**: Efficient batched encoding (32 items at a time)
- **Text Preparation**: Combines title + description for richer semantics
- **Metadata Tracking**: Preserves code, title, category for retrieval results
- **Code-to-Index Mapping**: Fast lookup from medical code to embedding row
- **Statistics**: Timing, dimensionality, model info

## Architecture

### EmbeddingsBuilder Class

**Initialization:**
```python
builder = EmbeddingsBuilder(
    model_name="all-MiniLM-L6-v2",  # HF model
    batch_size=32,
    device="cpu",  # or "cuda"
    logger=logger
)
```

**Key Methods:**

- `load_kb_from_json(kb_json_path)` - Load KB from Module 1
- `build(kb_json_path, output_dir)` - Generate embeddings and save outputs
- `load_embeddings(embeddings_dir)` - Reload previously saved embeddings

### Output Files

1. **embeddings.npy**: (71,704 x 384) numpy array of embeddings
2. **item_metadata.json**: List of {embeddings_id, code, title, description, category}
3. **code_to_index.json**: Dictionary mapping code → embedding row index
4. **metadata.json**: Model info (model_name, embedding_dim, num_embeddings, timestamp)
5. **stats.json**: Timing and statistics

## Data Flow

```
KB Item (from Module 1)
├─ code: "A000"
├─ title: "Cholera due to Vibrio cholerae..."
├─ description: "Acute cholera with severe dehydration"
└─ category: "Infectious"

↓ (Text Preparation)

Text: "Cholera due to Vibrio cholerae... Acute cholera with severe dehydration"

↓ (SentenceTransformer.encode)

Embedding: [0.123, -0.456, 0.789, ..., 0.234]  (384 dimensions)

↓ (Save)

embeddings.npy: Row 0 = [0.123, -0.456, 0.789, ..., 0.234]
item_metadata.json: [{embeddings_id: 0, code: "A000", title: "...", ...}]
code_to_index.json: {"A000": 0}
```

## Model Info: all-MiniLM-L6-v2

- **Type**: Sentence Transformer (bi-encoder)
- **Dimensions**: 384
- **Training Data**: MS MARCO + NLI datasets
- **Use Case**: Semantic similarity, retrieval tasks
- **Latency**: ~2-3ms per item on CPU, <1ms on GPU
- **Size**: ~22MB

## Installation

```bash
# Install dependencies
pip install sentence-transformers torch numpy

# Or use conda
conda install -c conda-forge sentence-transformers torch numpy
```

## Usage Example

```python
from pathlib import Path
from embeddings_builder import EmbeddingsBuilder
import logging

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize builder
builder = EmbeddingsBuilder(
    model_name="all-MiniLM-L6-v2",
    batch_size=32,
    device="cpu",
    logger=logger
)

# Build embeddings
kb_path = Path("../module_1_data_kb/output/kb.json")
output_dir = Path("output")
stats = builder.build(kb_path, output_dir)

print(f"Embedded {stats.embedded_items} items in {stats.embedding_time_seconds:.2f}s")

# Load later
embeddings, metadata, code_to_index = builder.load_embeddings(output_dir)
print(f"Loaded embeddings: {embeddings.shape}")
```

## Performance

For 71,704 ICD-10 items:

| Device | Time (approx) | Speed |
|--------|---------------|-------|
| CPU    | 10-15 minutes | ~80-120 items/sec |
| GPU    | 2-3 minutes   | ~400-600 items/sec |

## Next Steps

Module 3 (Vector Index) will:
1. Load the embeddings matrix
2. Build a FAISS ANN index (IVF or HNSW)
3. Enable fast nearest-neighbor retrieval

Module 4 will:
1. Encode user queries using the same model
2. Query the FAISS index for top-K candidates

## Testing

Run the test suite:
```bash
python test_module2.py
```

Expected output:
```
[OK] EmbeddingsBuilder Initialization
[OK] KB loaded (71704 items)
[OK] Embeddings built successfully
[OK] All 5 output files verified
[OK] Embeddings shape: (71704, 384)
[OK] All tests passed!
```

## Debugging

**Issue**: `ImportError: sentence-transformers not installed`
- Solution: `pip install sentence-transformers`

**Issue**: Out of memory
- Solution: Reduce `batch_size` (e.g., 16 instead of 32)

**Issue**: Slow on CPU
- Solution: Use GPU (`device="cuda"`) or reduce batch size and increase number of workers

## Dependencies

- `sentence-transformers>=2.6.0` - Bi-encoder models
- `torch>=2.0.0` - PyTorch backend
- `numpy>=1.24.0` - Array operations
- `transformers>=4.30.0` - HuggingFace models (auto-installed with sentence-transformers)
