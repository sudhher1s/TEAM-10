# Module 4: Query Encoder

Encodes user queries using the same model as Module 2 (`all-MiniLM-L6-v2`) and searches the FAISS index from Module 3.

## Quick Start

1. Ensure Module 3 output exists in `working_modules/output/`:
   - `faiss.index`
   - `item_metadata.json`

2. Run the demo:

```python
from pathlib import Path
from module_4_query_encoder.src.query_encoder import QueryEncoder

encoder = QueryEncoder(
    index_path=Path(r"c:\MY PROJECTS\GEN AI\working_modules\output\faiss.index"),
    item_metadata_path=Path(r"c:\MY PROJECTS\GEN AI\working_modules\output\item_metadata.json"),
)

res = encoder.search("chest pain", top_k=5)
print(f"Query took {res.elapsed_ms:.2f} ms")
for item in res.items:
    print(item.code, item.title, f"score={item.score:.4f}")
```

## Notes
- Uses L2 metric in FAISS; we convert distance to similarity via `1/(1+d)`.
- Normalizes query vectors to match Module 2 normalization.
- Top-K typically returns relevant ICD-10 codes semantically close to the query.
