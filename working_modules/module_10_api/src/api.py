from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator

app = FastAPI(title="Module 10: Medical Coding API", version="1.0")

class QueryRequest(BaseModel):
    query: str
    retrieve_k: int = 100
    rerank_k: int = 10
    provider: str = "mock"  # "openai" or "mock"
    model: Optional[str] = "gpt-3.5-turbo"
    index_path: Optional[str] = "c:/MY PROJECTS/GEN AI/working_modules/module_3_vector_index/index.faiss"
    metadata_path: Optional[str] = "c:/MY PROJECTS/GEN AI/working_modules/module_2_embeddings/item_metadata.json"
    kb_path: Optional[str] = "c:/MY PROJECTS/GEN AI/working_modules/module_1_data_kb/output/kb.json"

class QueryResponse(BaseModel):
    query: str
    retrieve: dict
    rerank: dict
    evidence: dict
    guardrails: dict
    grounded: dict

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/code")
async def code(req: QueryRequest) -> QueryResponse:
    orchestrator = MedicalCodingOrchestrator(
        index_path=Path(req.index_path),
        item_metadata_path=Path(req.metadata_path),
        kb_path=Path(req.kb_path),
        llm_model=req.model or "gpt-3.5-turbo",
        llm_provider=req.provider,
    )
    result = orchestrator.run(
        query=req.query,
        retrieve_k=req.retrieve_k,
        rerank_k=req.rerank_k,
    )
    return QueryResponse(**result)

# Serve frontend UI
app.mount("/", StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "static"), html=True), name="static")
