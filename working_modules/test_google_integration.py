"""
Quick test of integrated pipeline with Google Gemini
"""
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator

print("=" * 80)
print("INTEGRATION TEST: Google Gemini + Full Pipeline")
print("=" * 80)

# Initialize with Google provider
kb_path = WORKSPACE_ROOT / "working_modules" / "module_1_data_kb" / "output" / "kb.json"
index_path = WORKSPACE_ROOT / "working_modules" / "output" / "faiss.index"
metadata_path = WORKSPACE_ROOT / "working_modules" / "output" / "item_metadata.json"

print("\n🔧 Initializing orchestrator with Google Gemini...")
orchestrator = MedicalCodingOrchestrator(
    index_path=index_path,
    item_metadata_path=metadata_path,
    kb_path=kb_path,
    llm_model="gemini-2.5-flash",
    llm_provider="google",
)
print("✅ Orchestrator initialized!")

# Test query
query = "Patient with chest pain and ST elevation on ECG"
print(f"\n📋 Test Query: {query}")
print("\n🚀 Running full pipeline...")

result = orchestrator.run(query, retrieve_k=50, rerank_k=5)

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

print(f"\n✅ Retrieve: {result['retrieve']['top_codes'][:3]}")
print(f"✅ Rerank: {result['rerank']['top_codes'][:3]}")
print(f"✅ Evidence: {len(result['evidence']['items'])} items")
print(f"✅ Guardrails: {'VALID' if result['guardrails']['is_valid'] else 'INVALID'}")

grounded = result['grounded']
print(f"\n🤖 Grounding Results:")
print(f"   Model: {grounded['model']}")
print(f"   Codes: {grounded['codes']}")
print(f"   Confidence: {grounded['confidence']}%")
print(f"   Safe: {grounded['is_safe']}")

print(f"\n📝 Explanation:")
print("─" * 80)
explanation = grounded['explanation']
clean = explanation.replace("```json", "").replace("```", "").strip()
print(clean[:600])
print("─" * 80)

print("\n✅ INTEGRATION TEST COMPLETE!")
