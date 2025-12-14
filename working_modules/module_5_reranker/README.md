# Module 5: Cross-Encoder Reranker

Re-ranks the top-N candidates from Module 4 using a cross-encoder (`ms-marco-MiniLM-L-6-v2`) for improved precision.

## Quick Start

```python
from pathlib import Path
from working_modules.module_4_query_encoder.src.query_encoder import QueryEncoder
from working_modules.module_5_reranker.src.reranker import Reranker

encoder = QueryEncoder(
    index_path=Path(r"c:\MY PROJECTS\GEN AI\working_modules\output\faiss.index"),
    item_metadata_path=Path(r"c:\MY PROJECTS\GEN AI\working_modules\output\item_metadata.json"),
)

# Retrieve top-50 from FAISS
res = encoder.search("myocardial infarction with st elevation", top_k=50)

# Prepare candidates for reranker (list of dicts)
candidates = [
    {"code": it.code, "title": it.title, "category": it.category, "index_id": it.index_id}
    for it in res.items
]

reranker = Reranker()
rres = reranker.rerank(res.query, candidates, top_k=10)
print(f"Rerank took {rres.elapsed_ms:.2f} ms")
for item in rres.items:
    print(item.code, item.title, f"score={item.score:.4f}")
```

## Notes
- Cross-encoder inspects query–candidate pairs, generally improving ranking quality.
- Recommended: retrieve `top_k=50..200` from FAISS, then rerank to `top_k=10..20`.
- Model downloads on first run; cache thereafter.
