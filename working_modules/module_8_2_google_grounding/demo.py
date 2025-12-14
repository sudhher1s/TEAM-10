"""
Demo: Google Gemini Grounding Module 8.2
Shows how to use GoogleGrounder for medical code recommendations.
"""
import sys
from pathlib import Path

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_8_2_google_grounding.src.google_grounder import GoogleGrounder

def demo_google_grounding():
    """Demonstrate Google Gemini-based grounding."""
    
    print("=" * 70)
    print("MODULE 8.2: GOOGLE GEMINI GROUNDING DEMO")
    print("=" * 70)
    
    # Sample clinical evidence
    evidence = [
        {
            "code": "I2101",
            "title": "STEMI involving left main coronary artery",
            "description": "ST elevation myocardial infarction of left main coronary artery",
            "aliases": ["MI", "heart attack", "acute MI"],
            "relevance_score": 0.87,
        },
        {
            "code": "I2111",
            "title": "STEMI involving right coronary artery",
            "description": "ST elevation myocardial infarction of RCA",
            "aliases": ["STEMI", "acute coronary syndrome"],
            "relevance_score": 0.81,
        },
        {
            "code": "I214",
            "title": "Non-ST elevation myocardial infarction",
            "description": "NSTEMI - myocardial infarction without ST elevation",
            "aliases": ["NSTEMI"],
            "relevance_score": 0.45,
        },
    ]
    
    # Sample clinical query
    query = "Patient presents with acute chest pain, ST elevation on EKG, elevated troponin"
    
    print(f"\n📋 Clinical Query:\n{query}\n")
    print(f"🔍 Retrieved Evidence: {len(evidence)} ICD-10 codes\n")
    
    # Initialize grounder (will use GOOGLE_API_KEY if available, else mock)
    grounder = GoogleGrounder(provider="google")
    
    print(f"⚙️  Provider: {grounder.provider}")
    print(f"🤖 Model: {grounder.model}")
    print(f"🔌 API Client: {'Connected' if grounder.client else 'Mock Mode'}\n")
    
    print("-" * 70)
    print("🧠 CALLING GEMINI API...")
    print("-" * 70)
    
    # Get grounded recommendations
    result = grounder.ground(query, evidence)
    
    print(f"\n✅ Response received in {result.elapsed_ms:.0f}ms")
    print(f"🎯 Model Used: {result.model_used}")
    print(f"📊 Confidence: {result.confidence:.1%}\n")
    
    print("=" * 70)
    print("RECOMMENDED ICD-10 CODES")
    print("=" * 70)
    
    if result.codes:
        for i, code in enumerate(result.codes, 1):
            print(f"{i}. {code}")
    else:
        print("(No specific codes recommended)")
    
    print("\n" + "=" * 70)
    print("CLINICAL EXPLANATION")
    print("=" * 70)
    print(result.explanation)
    
    # Demo with guardrails
    print("\n\n" + "=" * 70)
    print("DEMO: GROUNDING WITH GUARDRAILS")
    print("=" * 70)
    
    guardrails_result = {
        "is_valid": True,
        "violations": [
            {"severity": "WARNING", "message": "High-risk diagnosis requires physician review"},
            {"severity": "INFO", "message": "Consider consulting cardiology"},
        ]
    }
    
    safe_result = grounder.ground_with_guardrails(query, evidence, guardrails_result)
    
    print(f"\n🛡️  Safety Check: {'✅ SAFE' if safe_result.is_safe else '❌ BLOCKED'}")
    print(f"⚠️  Warnings: {len(safe_result.warnings)}")
    
    for warning in safe_result.warnings:
        print(f"   - {warning}")
    
    print(f"\n📋 Recommended Codes: {safe_result.llm_response.codes}")
    print(f"📊 Confidence: {safe_result.llm_response.confidence:.1%}")
    
    print("\n" + "=" * 70)
    print("✅ MODULE 8.2 DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_google_grounding()
