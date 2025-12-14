# Module 7: Guardrails & Compliance Checker

Validates medical codes against compliance rules, coding standards, and clinical guidelines before LLM response generation.

## Purpose

**Problem**: Retrieved codes may violate medical coding standards (HIPAA, specificity rules, clinical coherence).

**Solution**: Apply policy checks to:
- Validate code format (ICD-10 compliance)
- Check specificity (avoid unspecified codes when specific ones exist)
- Enforce category limits (max codes per section)
- Flag clinical contradictions
- Generate compliance warnings/errors

## Rules Implemented

### 1. Code Format Validation
- Code must start with letter
- Must follow ICD-10 format (e.g., `A00.0`, `I2101`)
- **Severity**: ERROR

### 2. Code Specificity
- Flags unspecified codes (`unspecified`, `nos`, `nec`)
- Recommends more specific codes if available
- **Severity**: WARNING

### 3. Category Code Limits
- Infectious (A00-B99): max 3 codes
- Circulatory (I00-I99): max 5 codes
- Respiratory (J00-J99): max 4 codes
- **Severity**: WARNING

### 4. Clinical Coherence
- Flags incompatible code combinations
- Example: pregnancy codes + male-only codes
- **Severity**: WARNING

## Quick Start

```python
from pathlib import Path
from working_modules.module_7_guardrails.src.guardrails_checker import GuardrailsChecker

checker = GuardrailsChecker()

# Check codes
result = checker.check(
    query="chest pain with shortness of breath",
    codes=["I2101", "I2101", "R0602"],  # I2101 repeated
    titles=["STEMI left main", "STEMI left main", "Dyspnea"]
)

print(f"Valid: {result.is_valid}")
for violation in result.violations:
    print(f"  [{violation.severity}] {violation.rule_name}: {violation.message}")
    if violation.recommendation:
        print(f"    Recommendation: {violation.recommendation}")
```

## Output

```
Valid: True
  [warning] Code Specificity: Code 'I2101' is unspecified
    Recommendation: Consider using a more specific code...
```

## Integration with Pipeline

```python
# M4 -> M5 -> M6 -> M7 -> M8 (LLM)
encoder = QueryEncoder(...)
res = encoder.search(query, top_k=100)

reranker = Reranker()
rres = reranker.rerank(res.query, candidates, top_k=10)

extractor = EvidenceExtractor(kb_path)
evidence = extractor.extract(res.query, rres.items)

# NEW: Apply guardrails
checker = GuardrailsChecker()
guard_result = checker.check(
    res.query,
    [ev.code for ev in evidence.items],
    [ev.title for ev in evidence.items]
)

if guard_result.is_valid:
    # Safe to pass to LLM
    print("Codes passed guardrails check")
else:
    print("Warnings/errors detected:")
    for v in guard_result.violations:
        print(f"  {v.message}")
```
