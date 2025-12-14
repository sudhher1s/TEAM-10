# Module 10: Medical Coding API

FastAPI service that exposes Module 9 orchestrator.

## Endpoints
- GET `/health`: service status
- POST `/code`: run end-to-end pipeline

## Request Body (POST /code)
```
{
  "query": "Patient presents with acute cholera infection",
  "retrieve_k": 100,
  "rerank_k": 10,
  "provider": "mock",  // or "openai"
  "model": "gpt-3.5-turbo",
  "index_path": "c:/MY PROJECTS/GEN AI/working_modules/module_3_vector_index/index.faiss",
  "metadata_path": "c:/MY PROJECTS/GEN AI/working_modules/module_2_embeddings/item_metadata.json",
  "kb_path": "c:/MY PROJECTS/GEN AI/working_modules/module_1_data_kb/output/kb.json"
}
```

## Run Locally
```bash
python working_modules/module_10_api/scripts/run_api.py
```
- Health: http://127.0.0.1:8001/health
- Code: POST http://127.0.0.1:8001/code

## Example curl
```bash
curl -X POST http://127.0.0.1:8001/code \
  -H "Content-Type: application/json" \
  -d '{
        "query": "Patient presents with acute cholera infection",
        "provider": "mock",
        "kb_path": "c:/MY PROJECTS/GEN AI/working_modules/module_1_data_kb/output/kb.json"
      }'
```

## Notes
- Uses the resilient orchestrator fallbacks when FAISS or sentence-transformers are unavailable.
- OpenAI mode requires `OPENAI_API_KEY` environment variable.
