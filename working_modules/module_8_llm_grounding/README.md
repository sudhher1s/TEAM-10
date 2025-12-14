# Module 8: LLM Grounding

Generates clinically-grounded responses using OpenAI or Claude APIs. Responses are grounded in retrieved evidence (M6) and validated by guardrails (M7).

## Setup

Install OpenAI:
```bash
pip install openai
```

Set API key (one of):
```bash
export OPENAI_API_KEY=sk-...
# or
python -c "import openai; openai.api_key = 'sk-...'"
```

## Quick Start

```python
from working_modules.module_8_llm_grounding.src.llm_grounder import LLMGrounder

grounder = LLMGrounder(model="gpt-3.5-turbo")

evidence = [
    {
        "code": "I2101",
        "title": "STEMI involving left main coronary artery",
        "description": "ST elevation myocardial infarction...",
        "aliases": ["MI", "heart attack"]
    },
    {
        "code": "I2111",
        "title": "STEMI involving right coronary artery",
        "description": "...",
        "aliases": ["Right coronary STEMI"]
    }
]

# Generate response
result = grounder.ground(
    query="patient with chest pain and ST elevation",
    evidence=evidence
)

print(f"Recommended codes: {result.codes}")
print(f"Confidence: {result.confidence:.2%}")
print(f"\nExplanation:\n{result.explanation}")
```

## With Guardrails

```python
from working_modules.module_7_guardrails.src.guardrails_checker import GuardrailsChecker

checker = GuardrailsChecker()
guard_result = checker.check(
    query,
    codes=[ev["code"] for ev in evidence],
    titles=[ev["title"] for ev in evidence]
)

# Combine guardrails with LLM response
grounded = grounder.ground_with_guardrails(
    query,
    evidence,
    {
        "violations": [v.__dict__ for v in guard_result.violations],
        "is_valid": guard_result.is_valid
    }
)

if grounded.is_safe:
    print("✅ Safe to use")
else:
    print("⚠️ Warnings:")
    for w in grounded.warnings:
        print(f"  {w}")
```

## Full Pipeline (M4→M5→M6→M7→M8)

```python
# Setup
encoder = QueryEncoder(...)
reranker = Reranker()
extractor = EvidenceExtractor(kb_path)
checker = GuardrailsChecker()
grounder = LLMGrounder(model="gpt-3.5-turbo")

# Query
query = "chest pain with shortness of breath"

# M4: Retrieve
res = encoder.search(query, top_k=100)

# M5: Rerank
candidates = [{"code": it.code, "title": it.title, ...} for it in res.items]
rres = reranker.rerank(query, candidates, top_k=10)

# M6: Extract evidence
evidence = extractor.extract(query, [{"code": it.code, "score": it.score} for it in rres.items])

# M7: Check guardrails
guard = checker.check(query, [ev.code for ev in evidence.items], [ev.title for ev in evidence.items])

# M8: Generate grounded response
grounded = grounder.ground_with_guardrails(
    query,
    [ev.__dict__ for ev in evidence.items],
    {
        "violations": [v.__dict__ for v in guard.violations],
        "is_valid": guard.is_valid
    }
)

print(f"Codes: {grounded.llm_response.codes}")
print(f"Confidence: {grounded.llm_response.confidence:.2%}")
print(f"Explanation:\n{grounded.llm_response.explanation}")
```

## Models Supported

- **OpenAI**: gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **Claude** (planned): claude-2, claude-instant

## Output Format

```json
{
  "query": "chest pain with ST elevation",
  "response_text": "...",
  "codes": ["I2101", "I2111"],
  "explanation": "Based on the evidence...",
  "confidence": 0.85,
  "citations": ["I2101", "I2111"],
  "elapsed_ms": 1234,
  "model_used": "gpt-3.5-turbo"
}
```

## Notes

- LLM provides recommendations, not final diagnosis
- Always validate with medical professionals
- Temperature 0.3 = more deterministic/clinical
- Temperature 0.7 = more creative/varied
