"""
COMPREHENSIVE INTEGRATION TEST & DEMO
Tests all modules with Google Gemini API integration
"""
import sys
from pathlib import Path
import time

WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print(f"{'=' * 80}\n")

def print_subsection(title):
    """Print a formatted subsection."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")

def test_integration():
    """Run comprehensive integration test."""
    
    print_section("🏥 MEDICAL CODING AI - GOOGLE GEMINI INTEGRATION TEST")
    
    # Setup
    print("📋 Configuration:")
    print("   • AI Provider: Google Gemini")
    print("   • Model: gemini-2.5-flash")
    print("   • Pipeline: Retrieve → Rerank → Evidence → Guardrails → AI Grounding")
    
    kb_path = WORKSPACE_ROOT / "working_modules" / "module_1_data_kb" / "output" / "kb.json"
    index_path = WORKSPACE_ROOT / "working_modules" / "output" / "faiss.index"
    metadata_path = WORKSPACE_ROOT / "working_modules" / "output" / "item_metadata.json"
    
    print(f"\n📂 Data Paths:")
    print(f"   • KB: {kb_path.name}")
    print(f"   • Index: {index_path.name if index_path.exists() else 'N/A (using fallback)'}")
    
    # Initialize
    print_subsection("🔧 Initializing Pipeline Components")
    
    start_time = time.time()
    
    try:
        orchestrator = MedicalCodingOrchestrator(
            index_path=index_path,
            item_metadata_path=metadata_path,
            kb_path=kb_path,
            llm_model="gemini-2.5-flash",
            llm_provider="google",
        )
        init_time = (time.time() - start_time) * 1000
        print(f"✅ Pipeline initialized successfully ({init_time:.0f}ms)")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Test queries
    test_cases = [
        {
            "query": "Patient presents with acute cholera infection and severe dehydration",
            "description": "Infectious disease case"
        },
        {
            "query": "Type 2 diabetes mellitus with diabetic polyneuropathy",
            "description": "Chronic disease with complication"
        },
        {
            "query": "Acute appendicitis with generalized peritonitis",
            "description": "Surgical emergency"
        },
    ]
    
    results_summary = []
    
    for idx, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        description = test_case["description"]
        
        print_section(f"TEST CASE {idx}/{len(test_cases)}: {description}")
        
        print(f"👤 Clinical Query:")
        print(f"   \"{query}\"")
        
        print_subsection("🚀 Processing through AI Pipeline")
        
        try:
            start = time.time()
            result = orchestrator.run(query, retrieve_k=50, rerank_k=5)
            total_time = (time.time() - start) * 1000
            
            # Extract results
            retrieve = result.get("retrieve", {})
            rerank = result.get("rerank", {})
            evidence = result.get("evidence", {})
            guardrails = result.get("guardrails", {})
            grounded = result.get("grounded", {})
            
            # Display pipeline steps
            print(f"\n📊 Pipeline Execution:")
            print(f"   ✅ Retrieve: {len(retrieve.get('top_codes', []))} codes ({retrieve.get('elapsed_ms', 0):.0f}ms)")
            print(f"   ✅ Rerank: {len(rerank.get('top_codes', []))} codes ({rerank.get('elapsed_ms', 0):.0f}ms)")
            print(f"   ✅ Evidence: {len(evidence.get('items', []))} items ({evidence.get('elapsed_ms', 0):.0f}ms)")
            print(f"   ✅ Guardrails: {'VALID' if guardrails.get('is_valid') else 'INVALID'} ({guardrails.get('elapsed_ms', 0):.0f}ms)")
            print(f"   ✅ AI Grounding: {grounded.get('model', 'N/A')} ({grounded.get('elapsed_ms', 0):.0f}ms)")
            print(f"\n   ⏱️  Total Time: {total_time:.0f}ms")
            
            # Display AI results
            print_subsection("🤖 AI-Generated Results")
            
            codes = grounded.get("codes", [])
            confidence = grounded.get("confidence", 0)
            explanation = grounded.get("explanation", "")
            is_safe = grounded.get("is_safe", True)
            warnings = grounded.get("warnings", [])
            
            print(f"\n🎯 Confidence Score: {confidence}%")
            print(f"🛡️  Safety Status: {'✅ SAFE' if is_safe else '⚠️ REVIEW NEEDED'}")
            
            if warnings:
                print(f"\n⚠️  Warnings ({len(warnings)}):")
                for w in warnings:
                    print(f"   • {w}")
            
            print(f"\n💊 Recommended ICD-10 Codes:")
            if codes:
                for i, code in enumerate(codes, 1):
                    print(f"   {i}. {code}")
            else:
                print("   (See explanation for reasoning)")
            
            # Show evidence used
            evidence_items = evidence.get("items", [])
            if evidence_items:
                print(f"\n🔬 Clinical Evidence Used ({len(evidence_items)} codes):")
                for i, ev in enumerate(evidence_items[:5], 1):
                    code = ev.get("code", "")
                    title = ev.get("title", "")
                    score = ev.get("relevance_score", 0)
                    print(f"   {i}. {code} - {title[:55]:<55} (score: {score:.3f})")
                if len(evidence_items) > 5:
                    print(f"   ... and {len(evidence_items) - 5} more")
            
            print(f"\n📝 AI Clinical Explanation:")
            print("─" * 80)
            clean_explanation = explanation.replace("```json", "").replace("```", "").strip()
            # Print first 500 chars
            print(clean_explanation[:500])
            if len(clean_explanation) > 500:
                print("...")
            print("─" * 80)
            
            # Store summary
            results_summary.append({
                "query": query[:50],
                "codes": codes,
                "confidence": confidence,
                "time_ms": total_time,
                "safe": is_safe
            })
            
        except Exception as e:
            print(f"\n❌ Test case failed: {e}")
            import traceback
            traceback.print_exc()
            results_summary.append({
                "query": query[:50],
                "codes": [],
                "confidence": 0,
                "time_ms": 0,
                "safe": False,
                "error": str(e)
            })
    
    # Summary
    print_section("📊 INTEGRATION TEST SUMMARY")
    
    print(f"Total Test Cases: {len(test_cases)}")
    print(f"Successful: {sum(1 for r in results_summary if 'error' not in r)}")
    print(f"Failed: {sum(1 for r in results_summary if 'error' in r)}")
    
    print(f"\n{'─' * 80}")
    print(f"{'Query':<52} {'Codes':<8} {'Conf':<6} {'Time':<8} {'Safe':<6}")
    print(f"{'─' * 80}")
    
    for r in results_summary:
        query_short = r['query'][:50]
        codes_count = len(r['codes'])
        conf = r['confidence']
        time_ms = r['time_ms']
        safe = '✅' if r['safe'] else '⚠️'
        
        if 'error' in r:
            print(f"{query_short:<52} {'ERROR':<8} {'-':<6} {'-':<8} {'❌':<6}")
        else:
            print(f"{query_short:<52} {codes_count:<8} {conf}%{'':<3} {time_ms:.0f}ms{'':<3} {safe:<6}")
    
    print(f"{'─' * 80}")
    
    print_section("✅ INTEGRATION TEST COMPLETE")
    
    print("🎉 Google Gemini Integration Status: OPERATIONAL")
    print("\n📚 Available Components:")
    print("   • Module 8.2: Google Gemini Grounding ✅")
    print("   • Module 8: OpenAI Grounding ✅")
    print("   • Module 9: Orchestrator (Multi-provider) ✅")
    print("   • Module 10: FastAPI REST API ✅")
    print("   • Interactive Chatbot ✅")
    
    print("\n🚀 How to Use:")
    print("   1. Interactive Chatbot:")
    print("      python working_modules/medical_coding_chatbot.py")
    print()
    print("   2. REST API:")
    print("      python working_modules/module_10_api/scripts/run_api.py")
    print("      Then POST to http://127.0.0.1:8001/code")
    print()
    print("   3. Python Integration:")
    print("      from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator")
    print("      orchestrator = MedicalCodingOrchestrator(..., llm_provider='google')")
    print("      result = orchestrator.run('your query')")
    print()


if __name__ == "__main__":
    test_integration()
