# Module 6: Evidence Extraction

Retrieves rich context (title, description, aliases, category) for each retrieved code from the knowledge base. This context is passed to the LLM for grounded response generation.

## Purpose

**Problem**: After retrieval and reranking (M4-M5), you have only `code`, `title`, `score`. The LLM needs more context to explain *why* a code is relevant.

**Solution**: Extract full evidence from the KB:
- Title
- Description (clinical definition)
- Category (diagnostic, procedure, etc.)
- Aliases (alternate names, abbreviations)
- Relevance score (from reranker)

## Quick Start

```python
from pathlib import Path
from working_modules.module_4_query_encoder.src.query_encoder import QueryEncoder
from working_modules.module_5_reranker.src.reranker import Reranker
from working_modules.module_6_evidence_extraction.src.evidence_extractor import EvidenceExtractor

# M4: Retrieve
encoder = QueryEncoder(...)
res = encoder.search("myocardial infarction", top_k=100)
candidates = [{"code": it.code, "title": it.title, "category": it.category, "index_id": it.index_id} for it in res.items]

# M5: Rerank
reranker = Reranker()
rres = reranker.rerank(res.query, candidates, top_k=10)

# M6: Extract evidence
extractor = EvidenceExtractor(Path(r"c:\MY PROJECTS\GEN AI\working_modules\module_1_data_kb\output\kb.json"))
evidence = extractor.extract(res.query, [{"code": it.code, "score": it.score} for it in rres.items])

# Now LLM can use rich context
for ev in evidence.items:
    print(f"{ev.code} - {ev.title}")
    print(f"  Description: {ev.description}")
    print(f"  Aliases: {ev.aliases}")
    print(f"  Relevance: {ev.relevance_score:.4f}\n")
```

## Output Format

```python
EvidenceSet(
    query="myocardial infarction",
    items=[
        Evidence(
            code="I2101",
            title="STEMI involving left main coronary artery",
            description="ST elevation myocardial infarction (STEMI) of left main...",
            category="Diagnosis",
            aliases=["MI", "heart attack", "left main STEMI"],
            relevance_score=0.8234
        ),
        ...
    ],
    elapsed_ms=2.34
)
```
