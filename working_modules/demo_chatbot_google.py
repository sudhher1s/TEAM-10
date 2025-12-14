"""
Automated Demo of Medical Coding Chatbot with Google Gemini
"""
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator

def demo_chatbot():
    """Demonstrate the chatbot with pre-defined queries."""
    
    print("\n" + "=" * 80)
    print("🏥 MEDICAL CODING CHATBOT - GOOGLE GEMINI DEMO")
    print("=" * 80)
    
    # Initialize
    kb_path = WORKSPACE_ROOT / "working_modules" / "module_1_data_kb" / "output" / "kb.json"
    index_path = WORKSPACE_ROOT / "working_modules" / "output" / "faiss.index"
    metadata_path = WORKSPACE_ROOT / "working_modules" / "output" / "item_metadata.json"
    
    print("\n🔧 Initializing Medical Coding Pipeline...")
    print("   • Provider: GOOGLE GEMINI")
    print("   • Model: gemini-2.5-flash")
    
    orchestrator = MedicalCodingOrchestrator(
        index_path=index_path,
        item_metadata_path=metadata_path,
        kb_path=kb_path,
        llm_model="gemini-2.5-flash",
        llm_provider="google",
    )
    print("   ✅ Pipeline initialized!\n")
    
    # Test queries
    test_queries = [
        "Patient presents with acute cholera infection",
        "Type 2 diabetes mellitus with diabetic neuropathy",
        "Acute appendicitis with peritonitis",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print("\n" + "=" * 80)
        print(f"QUERY {i} of {len(test_queries)}")
        print("=" * 80)
        print(f"\n👤 Patient Case: {query}")
        print("\n🔍 Processing through AI pipeline...")
        
        try:
            result = orchestrator.run(query, retrieve_k=50, rerank_k=5)
            
            grounded = result.get("grounded", {})
            codes = grounded.get("codes", [])
            confidence = grounded.get("confidence", 0)
            model = grounded.get("model", "unknown")
            explanation = grounded.get("explanation", "")
            
            print(f"\n{'─' * 80}")
            print(f"🤖 AI Response (Model: {model})")
            print(f"{'─' * 80}")
            print(f"\n🎯 Confidence: {confidence}%")
            print(f"\n💊 Recommended ICD-10 Codes:")
            if codes:
                for j, code in enumerate(codes, 1):
                    print(f"   {j}. {code}")
            else:
                print("   (No specific codes - see explanation)")
            
            print(f"\n📝 Clinical Explanation:")
            print("─" * 80)
            clean = explanation.replace("```json", "").replace("```", "").strip()
            print(clean[:700])
            if len(clean) > 700:
                print("\n   ...")
            print("─" * 80)
            
            # Evidence
            evidence = result.get("evidence", {}).get("items", [])
            print(f"\n🔬 Evidence Retrieved: {len(evidence)} codes")
            for j, ev in enumerate(evidence[:3], 1):
                print(f"   {j}. {ev.get('code', '')} - {ev.get('title', '')[:50]}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        if i < len(test_queries):
            print("\n⏸️  Press Enter to continue to next query...")
            input()
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print("\n🎉 The Google Gemini integration is working!")
    print("   You can now use the interactive chatbot:")
    print("   python working_modules/medical_coding_chatbot.py\n")


if __name__ == "__main__":
    demo_chatbot()
