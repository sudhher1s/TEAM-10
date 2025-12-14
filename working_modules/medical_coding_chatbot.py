"""
Medical Coding Chatbot - Google Gemini Integration
Interactive command-line chatbot for medical coding assistance
"""
import sys
from pathlib import Path
import os

WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator

class MedicalCodingChatbot:
    def __init__(self, provider="google", model="gemini-2.5-flash"):
        """Initialize chatbot with Google Gemini or fallback to mock."""
        print("\n" + "=" * 80)
        print("🏥 MEDICAL CODING ASSISTANT - POWERED BY GOOGLE GEMINI")
        print("=" * 80)
        
        # Paths
        kb_path = WORKSPACE_ROOT / "working_modules" / "module_1_data_kb" / "output" / "kb.json"
        index_path = WORKSPACE_ROOT / "working_modules" / "output" / "faiss.index"
        metadata_path = WORKSPACE_ROOT / "working_modules" / "output" / "item_metadata.json"
        
        # Initialize orchestrator
        print("\n🔧 Initializing Medical Coding Pipeline...")
        print(f"   • Provider: {provider.upper()}")
        print(f"   • Model: {model}")
        print(f"   • Knowledge Base: {kb_path.name}")
        
        try:
            self.orchestrator = MedicalCodingOrchestrator(
                index_path=index_path,
                item_metadata_path=metadata_path,
                kb_path=kb_path,
                llm_model=model,
                llm_provider=provider,
            )
            print("   ✅ Pipeline initialized successfully!")
        except Exception as e:
            print(f"   ⚠️ Warning: {e}")
            print("   💡 Using fallback mode")
            self.orchestrator = MedicalCodingOrchestrator(
                index_path=index_path,
                item_metadata_path=metadata_path,
                kb_path=kb_path,
                llm_model=model,
                llm_provider="mock",
            )
        
        self.provider = provider
        self.conversation_history = []
    
    def process_query(self, query: str) -> dict:
        """Process a medical coding query through the pipeline."""
        print(f"\n{'─' * 80}")
        print(f"🔍 Processing Query...")
        print(f"{'─' * 80}")
        
        result = self.orchestrator.run(query, retrieve_k=100, rerank_k=10)
        self.conversation_history.append({"query": query, "result": result})
        
        return result
    
    def display_result(self, result: dict):
        """Display results in a user-friendly format."""
        grounded = result.get("grounded", {})
        codes = grounded.get("codes", [])
        confidence = grounded.get("confidence", 0)
        explanation = grounded.get("explanation", "")
        model = grounded.get("model", "unknown")
        is_safe = grounded.get("is_safe", True)
        warnings = grounded.get("warnings", [])
        
        print(f"\n{'═' * 80}")
        print(f"📊 RESULTS")
        print(f"{'═' * 80}")
        
        print(f"\n🤖 Model: {model}")
        print(f"🎯 Confidence: {confidence}%")
        print(f"🛡️  Safety: {'✅ SAFE' if is_safe else '⚠️ REVIEW NEEDED'}")
        
        if warnings:
            print(f"\n⚠️  Warnings:")
            for w in warnings:
                print(f"   • {w}")
        
        print(f"\n💊 Recommended ICD-10 Codes:")
        if codes:
            for i, code in enumerate(codes, 1):
                print(f"   {i}. {code}")
        else:
            print("   (No specific codes recommended)")
        
        print(f"\n📝 Clinical Explanation:")
        print("─" * 80)
        # Clean up JSON formatting if present
        clean_explanation = explanation.replace("```json", "").replace("```", "").strip()
        print(clean_explanation[:800])
        if len(clean_explanation) > 800:
            print("...")
        print("─" * 80)
        
        # Show evidence used
        evidence = result.get("evidence", {}).get("items", [])
        if evidence:
            print(f"\n🔬 Evidence Used ({len(evidence)} codes):")
            for i, ev in enumerate(evidence[:5], 1):
                code = ev.get("code", "")
                title = ev.get("title", "")
                score = ev.get("relevance_score", 0)
                print(f"   {i}. {code} - {title} (score: {score:.3f})")
            if len(evidence) > 5:
                print(f"   ... and {len(evidence) - 5} more")
    
    def run(self):
        """Start the interactive chatbot."""
        print(f"\n{'═' * 80}")
        print("💬 CHATBOT READY")
        print("═" * 80)
        print("\nI can help you find ICD-10 codes for medical conditions!")
        print("\nCommands:")
        print("  • Type your medical query to get coding recommendations")
        print("  • Type 'history' to see conversation history")
        print("  • Type 'quit' or 'exit' to end the session")
        print("\nExample queries:")
        print("  - Patient with acute myocardial infarction")
        print("  - Chest pain with ST elevation on EKG")
        print("  - Type 2 diabetes with neuropathy")
        
        while True:
            try:
                print(f"\n{'═' * 80}")
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using Medical Coding Assistant!")
                    print("   Stay safe and code accurately! 🏥\n")
                    break
                
                if user_input.lower() == 'history':
                    print(f"\n📜 Conversation History ({len(self.conversation_history)} queries):")
                    for i, item in enumerate(self.conversation_history, 1):
                        codes = item['result'].get('grounded', {}).get('codes', [])
                        print(f"\n{i}. Query: {item['query'][:60]}...")
                        print(f"   Codes: {codes}")
                    continue
                
                # Process the query
                result = self.process_query(user_input)
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye! 🏥\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("   Please try again with a different query.\n")


def main():
    """Main entry point for the chatbot."""
    # Check for Google API key
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if google_key:
        print("\n✅ GOOGLE_API_KEY detected - Using Google Gemini")
        provider = "google"
        model = "gemini-2.5-flash"
    else:
        print("\n⚠️  GOOGLE_API_KEY not found - Using Mock Mode")
        print("   Set GOOGLE_API_KEY environment variable to use Google Gemini")
        provider = "mock"
        model = "mock"
    
    chatbot = MedicalCodingChatbot(provider=provider, model=model)
    chatbot.run()


if __name__ == "__main__":
    main()
