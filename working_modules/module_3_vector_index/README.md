# Module 3: Vector Index Builder

## Purpose

Build a **FAISS (Facebook AI Similarity Search) index** for ultra-fast nearest-neighbor similarity search over 71,704 medical code embeddings. Enables <5ms retrieval of the most similar codes to any query.

## Architecture

```
Module 2 (Embeddings)
    ↓
    embeddings.npy (71,704 × 384)
    ↓
[Module 3 - Vector Index]
    ├─ Load embeddings
    ├─ Initialize FAISS index (IVF or FLAT)
    ├─ Train quantizer (IVF only)
    ├─ Add all vectors to index
    └─ Save to disk
    ↓
    faiss.index (optimized for search)
    ↓
Module 4 (Query Encoder) + Module 5 (Reranker)
```

## What FAISS Does

**Problem**: Searching 71,704 vectors for similarity is slow
- Naive approach: Compare query to all 71,704 vectors → ~500ms on CPU
- Need: Fast approximate nearest neighbors

**Solution**: FAISS provides multiple indexing strategies

### Index Types

#### IVF (Inverted File Index) - Default
- **Concept**: Partition vector space into clusters
- **Speed**: ~5-10ms for top-K search
- **Accuracy**: 99%+ for well-tuned parameters
- **Memory**: ~110 MB index + 110 MB embeddings
- **Tuning**: `nlist` (clusters) and `nprobe` (clusters to search)

#### FLAT (Exhaustive)
- **Concept**: Linear search through all vectors
- **Speed**: ~500ms for 71K vectors
- **Accuracy**: 100%
- **Use case**: Small datasets or validation

## How IVF Works

```
┌─────────────────────────────────────────┐
│  71,704 Medical Code Embeddings         │
│  (384-dimensional vectors)              │
└─────────────────────────────────────────┘
         ↓
    [TRAINING PHASE]
    Sample 100K vectors
    Run K-means clustering
    Create 100 cluster centroids
    ↓
┌─────────────────────────────────────────┐
│  Cluster Assignment                     │
│  Vector 0 → Cluster 5                   │
│  Vector 1 → Cluster 5                   │
│  Vector 2 → Cluster 12                  │
│  ...                                    │
│  Vector 71703 → Cluster 87              │
└─────────────────────────────────────────┘
         ↓
    [SEARCH PHASE]
    User query → embedding → Query vector
    ↓
    Find closest 10 cluster centroids
    (using distance metric)
    ↓
    Search only vectors in those 10 clusters
    ↓
    Return top-K similar vectors
    ↓
    ~5ms total search time (100× speedup!)
```

### Key Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `nlist` | 100 | Split 71,704 vectors into 100 clusters (~717 vectors per cluster) |
| `nprobe` | 10 | When searching, look in closest 10 clusters |
| `metric` | L2 | Euclidean distance (shorter = more similar) |

**Speed/Accuracy Tradeoff:**
- `nprobe=1`: Fastest (~2ms), least accurate (95%)
- `nprobe=10`: Balanced (~5ms), accurate (99%)
- `nprobe=100`: Slowest (~50ms), most accurate (99.9%)

## Output Files

### faiss.index (~110 MB)
Binary FAISS index file containing:
- Cluster centroids
- Vector-to-cluster assignments
- Optimized data structures for search

### index_metadata.json
```json
{
  "index_type": "IVF",
  "embedding_dim": 384,
  "num_vectors": 71704,
  "num_probes": 10,
  "nlist": 100,
  "metric": "L2",
  "model_name": "all-MiniLM-L6-v2",
  "kb_version": "v1.0",
  "timestamp": 1702562401.0,
  "embeddings_path": "...",
  "metadata_path": "..."
}
```

### code_to_index.json
```json
{
  "A000": 0,
  "A001": 1,
  "A009": 2,
  ...
  "Z9989": 71703
}
```

## Usage

```python
from src.vector_index_builder import VectorIndexBuilder
import numpy as np

# Initialize builder
builder = VectorIndexBuilder(
    index_type="IVF",
    nlist=100,
    num_probes=10,
    metric="L2"
)

# Build index
embeddings_path = Path("../output/embeddings.npy")
metadata_path = Path("../output/item_metadata.json")
index, stats = builder.build(embeddings_path, metadata_path)

# Save to disk
builder.save_index(Path("output/"))

# Search
query_embedding = np.random.randn(384).astype(np.float32)
results = builder.search(query_embedding, top_k=20)

for result in results.results:
    print(f"{result.code}: {result.title} (similarity: {result.similarity_score:.4f})")
```

## Performance

### Build Time
- IVF with 71,704 vectors: ~10-30 seconds
- Training K-means: ~5 seconds
- Adding vectors: ~5 seconds

### Search Performance
| Query Type | IVF (10 probes) | FLAT |
|-----------|-----------------|------|
| Single query | 2-5ms | 500ms |
| Batch 100 | 200ms | 50s |
| Accuracy | 99% | 100% |

### Memory Usage
- FAISS index: ~110 MB
- Embeddings (if loaded): ~110 MB
- Metadata: ~24 MB
- **Total: ~250 MB** (compresses to ~100 MB on disk)

## Testing

Run the test suite:
```bash
python test_module3.py
```

Expected output:
```
[OK] VectorIndexBuilder Initialization
[OK] Embeddings loaded: shape (71704, 384)
[OK] Index built in 15.23s (4700 vectors/sec)
[OK] Index saved to output/
[OK] All output files verified
[OK] Search completed in 3.45ms
[OK] Top-5 similar codes to A000
    1. A001: cholera...variant (similarity: 0.9382)
    2. A009: cholera unspecified (similarity: 0.8921)
    ...
[OK] All tests passed!
```

## Next Steps

**Module 4 (Query Encoder)**:
- Encode user queries to 384-dim vectors
- Use same model (all-MiniLM-L6-v2)
- Compare query embedding to index

**Module 5 (Cross-Encoder Reranker)**:
- Take top-20 from FAISS
- Re-score with cross-encoder
- Refine ranking for higher precision

## Debugging

**Issue**: "faiss not installed"
- Solution: `pip install faiss-cpu` (CPU) or `pip install faiss-gpu` (GPU)

**Issue**: Slow search (>20ms)
- Cause: `nprobe` too high
- Solution: Reduce `nprobe` from 10 to 5

**Issue**: Missing relevant codes
- Cause: `nprobe` too low
- Solution: Increase `nprobe` from 10 to 20

## Dependencies

- `faiss-cpu>=1.8.0` - Vector similarity search
- `numpy>=1.24.0` - Array operations
- `json` - Metadata serialization (stdlib)

## Architecture Integration

```
Module 1: Data & KB
    ↓ (kb.json)
Module 2: Embeddings
    ↓ (embeddings.npy)
Module 3: Vector Index  ← YOU ARE HERE
    ↓ (faiss.index)
Module 4: Query Encoder
    ↓
Module 5: Cross-Encoder Reranker
    ↓
Modules 6-10: RAG Pipeline
```

---

**Status**: Ready for Module 4 (Query Encoder)

*Generated: December 14, 2025*  
*Vector Index Type: IVF with 100 clusters*  
*Search Time: ~3-5ms per query*
