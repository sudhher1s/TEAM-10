import sys
from pathlib import Path
import os

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_4_query_encoder.src.query_encoder import QueryEncoder
from working_modules.module_5_reranker.src.reranker import Reranker
from working_modules.module_6_evidence_extraction.src.evidence_extractor import EvidenceExtractor
from working_modules.module_7_guardrails.src.guardrails_checker import GuardrailsChecker
from working_modules.module_8_llm_grounding.src.llm_grounder import LLMGrounder

OUTPUT_DIR = Path(r"c:\MY PROJECTS\GEN AI\working_modules\output")
KB_PATH = Path(r"c:\MY PROJECTS\GEN AI\working_modules\module_1_data_kb\output\kb.json")
INDEX_PATH = OUTPUT_DIR / "faiss.index"
ITEM_META_PATH = OUTPUT_DIR / "item_metadata.json"

print("=" * 80)
print("FULL M4→M5→M6→M7→M8 PIPELINE DEMO")
print("=" * 80)

# Initialize all modules
print("\n[INIT] Initializing modules...")
encoder = QueryEncoder(index_path=INDEX_PATH, item_metadata_path=ITEM_META_PATH)
reranker = Reranker()
extractor = EvidenceExtractor(KB_PATH)
checker = GuardrailsChecker()
grounder = LLMGrounder(model="gpt-3.5-turbo")
print("✅ All modules initialized")

# User query
query = "patient with sudden onset chest pain, shortness of breath, and ST elevation on ECG"

print(f"\n{'=' * 80}")
print(f"QUERY: {query}")
print(f"{'=' * 80}")

# M4: Retrieve
print("\n[M4] Query Encoder - Retrieving top-100 candidates...")
res = encoder.search(query, top_k=100)
print(f"✅ Retrieved {len(res.items)} codes in {res.elapsed_ms:.1f}ms")
print(f"   Top-3: {[it.code for it in res.items[:3]]}")

# M5: Rerank
print("\n[M5] Reranker - Re-scoring top-100 to top-10...")
candidates = [
    {"code": it.code, "title": it.title, "category": it.category, "index_id": it.index_id}
    for it in res.items
]
rres = reranker.rerank(query, candidates, top_k=10)
print(f"✅ Reranked in {rres.elapsed_ms:.1f}ms")
print(f"   Top-3: {[(it.code, f'{it.score:.4f}') for it in rres.items[:3]]}")

# M6: Extract Evidence
print("\n[M6] Evidence Extraction - Getting full context...")
evidence = extractor.extract(
    query,
    [{"code": it.code, "score": it.score} for it in rres.items]
)
print(f"✅ Extracted evidence in {evidence.elapsed_ms:.1f}ms")
for i, ev in enumerate(evidence.items[:3], 1):
    print(f"   {i}. {ev.code} - {ev.title}")

# M7: Guardrails
print("\n[M7] Guardrails - Checking compliance...")
guard = checker.check(
    query,
    [ev.code for ev in evidence.items],
    [ev.title for ev in evidence.items]
)
print(f"✅ Checked guardrails in {guard.elapsed_ms:.1f}ms")
print(f"   Valid: {guard.is_valid}")
if guard.violations:
    print(f"   Violations: {len(guard.violations)}")
    for v in guard.violations[:2]:
        print(f"     - [{v.severity}] {v.message}")

# M8: LLM Grounding
print("\n[M8] LLM Grounding - Generating explanation...")
try:
    grounded = grounder.ground_with_guardrails(
        query,
        [ev.__dict__ for ev in evidence.items],
        {
            "violations": [v.__dict__ for v in guard.violations],
            "is_valid": guard.is_valid
        }
    )
    print(f"✅ Generated response in {grounded.llm_response.elapsed_ms:.1f}ms")
    print(f"   Model: {grounded.llm_response.model_used}")
    print(f"   Confidence: {grounded.llm_response.confidence:.2%}")
    print(f"   Recommended codes: {grounded.llm_response.codes}")
    print(f"\n   Explanation:")
    print(f"   {grounded.llm_response.explanation[:500]}...")
    if not grounded.is_safe:
        print(f"\n   ⚠️ Safety warnings:")
        for w in grounded.warnings:
            print(f"      {w}")
except Exception as e:
    print(f"⚠️ LLM Error: {e}")
    print(f"   (Check OpenAI billing at https://platform.openai.com/account/billing)")

print(f"\n{'=' * 80}")
print("✅ FULL PIPELINE DEMONSTRATION COMPLETE")
print(f"{'=' * 80}")
