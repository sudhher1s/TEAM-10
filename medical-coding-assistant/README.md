# Healthcare H10: Medical Coding Assistant

Map short de-identified notes to ICD-10 codes using hybrid retrieval (BM25 + embeddings) and reranking, with evidence spans and safety guardrails.

## Problem Statement
"Map short de-identified notes to ICD10 codes (top-k retrieval + rerank). Sample data: MIMICIII Clinical Notes. Outcome: Prototype retrieval over small sample; output code candidates + justification spans. Stack: Python, LangChain, embeddings, BM25, reranker optional."

## Datasets
- `data/raw/ICD10codes.csv` (no header): `A00,0,A000,"full desc","alt desc","category"`
- `data/raw/icd9to10dictionary.txt` (no header): `001.0|A00.0|description`

If the raw files are present at the workspace root, the loader will copy/link them automatically.

## Architecture
```
LOAD → KB (merge ICD10 + ICD9→10) → INDEX (BM25 + Embeddings)
   → RETRIEVE (hybrid) → RERANK (cross-encoder/LLM) → EVIDENCE → GUARDRAILS → OUTPUT
```

## Quickstart
1. Install deps:
```
pip install -r requirements.txt
```
2. Build index:
```
python scripts/01_build_index.py
```

## Use the MIMIC-III demo dataset

This repo includes a demo MIMIC-III folder at `mimic-iii-clinical-database-demo-1.4/`.

1) Prepare an evaluation set by joining discharge notes with diagnoses and mapping ICD-9→ICD-10:

```
& "D:/GEN AI/.venv/Scripts/python.exe" "scripts/04_prepare_mimic.py"
```

This writes `data/processed/mimic_eval.tsv`.

2) Evaluate the pipeline on that set:

```
& "D:/GEN AI/.venv/Scripts/python.exe" "scripts/05_eval_mimic.py"
```

Both scripts use only the Python standard library and the existing BM25 index, so they work on Python 3.14 without compiled dependencies.
3. Run API:
```
uvicorn api.main:app --reload
```
4. Predict demo:
```
python scripts/03_predict_demo.py
```

## API Demo
```
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"note_text":"Patient with chest pain, SOB, EKG ST elevation","top_k":5}'
```

## Evaluation
Open the notebook:
```
jupyter notebooks/evaluation.ipynb
```
Outputs Top-1/3/5, MRR, P@5, R@5, latency, and case studies.

## Limitations & Ethics
- Not medical advice. Coding assistance only.
- May miss rare codes; use as decision support.
- De-identified notes only. Detect and reject PHI.

## Demo Outline (10 min)
- Intro + problem
- Data + KB build
- Hybrid retrieval
- Rerank + evidence
- Guardrails
- API live demo
- Metrics + failures
- Next steps
