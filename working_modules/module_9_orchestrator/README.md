# Module 9: Orchestrator

Chains retrieval (Module 4), reranking (Module 5), evidence extraction (Module 6), guardrails (Module 7), and LLM grounding (Module 8) into a single callable.

## Use Cases
- Single entrypoint to get grounded codes and explanations
- Switchable LLM provider: `openai` or `mock` for offline/testing
- Returns structured outputs useful for API (Module 10)

## Quick Start

### Prereqs
- Built FAISS index and metadata from Modules 2–3
- KB file from Module 6

### CLI
```bash
python working_modules/module_9_orchestrator/scripts/run_orchestrator.py \
  --query "Patient presents with acute cholera infection" \
  --index "c:/MY PROJECTS/GEN AI/working_modules/module_3_vector_index/index.faiss" \
  --metadata "c:/MY PROJECTS/GEN AI/working_modules/module_2_embeddings/item_metadata.json" \
  --kb "c:/MY PROJECTS/GEN AI/working_modules/module_6_evidence/kb.json" \
  --provider mock \
  --retrieve_k 100 \
  --rerank_k 10
```

### Python
```python
from pathlib import Path
from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator

orchestrator = MedicalCodingOrchestrator(
    index_path=Path("c:/MY PROJECTS/GEN AI/working_modules/module_3_vector_index/index.faiss"),
    item_metadata_path=Path("c:/MY PROJECTS/GEN AI/working_modules/module_2_embeddings/item_metadata.json"),
    kb_path=Path("c:/MY PROJECTS/GEN AI/working_modules/module_6_evidence/kb.json"),
    llm_provider="mock",
)

result = orchestrator.run("Patient presents with acute cholera infection")
print(result["grounded"]["codes"], result["grounded"]["confidence"]) 
```

## Notes
- OpenAI mode: set `OPENAI_API_KEY` env and `--provider openai`
- Mock mode: deterministic, safe output useful for tests
- Ideal feeder for Module 10 API
