import sys
from pathlib import Path
import os

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Test 1: Check API key
print("=" * 60)
print("TEST 1: Checking OpenAI API Key")
print("=" * 60)

api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    print(f"✅ API Key is set")
    print(f"   Key preview: {api_key[:20]}...{api_key[-10:]}")
else:
    print("❌ API Key not found in environment")
    sys.exit(1)

# Test 2: Check OpenAI library
print("\n" + "=" * 60)
print("TEST 2: Checking OpenAI Library")
print("=" * 60)

try:
    import openai
    openai.api_key = api_key
    print(f"✅ OpenAI library imported successfully")
    print(f"   Version: {openai.__version__}")
except ImportError as e:
    print(f"❌ OpenAI library not found: {e}")
    sys.exit(1)

# Test 3: Module 8 basic test
print("\n" + "=" * 60)
print("TEST 3: Module 8 LLM Grounder with Mock Data")
print("=" * 60)

try:
    from working_modules.module_8_llm_grounding.src.llm_grounder import LLMGrounder
    
    grounder = LLMGrounder(model="gpt-3.5-turbo")
    
    evidence = [
        {
            "code": "I2101",
            "title": "STEMI involving left main coronary artery",
            "description": "ST elevation myocardial infarction of left main coronary artery",
            "aliases": ["MI", "heart attack", "STEMI"]
        },
        {
            "code": "I2111",
            "title": "STEMI involving right coronary artery",
            "description": "ST elevation myocardial infarction of right coronary artery",
            "aliases": ["Right coronary STEMI", "RCA STEMI"]
        }
    ]
    
    print("Calling LLM with query: 'patient with chest pain and ST elevation'")
    result = grounder.ground(
        query="patient with chest pain and ST elevation",
        evidence=evidence
    )
    
    print(f"✅ LLM Response received")
    print(f"   Codes: {result.codes}")
    print(f"   Confidence: {result.confidence:.2%}")
    print(f"   Latency: {result.elapsed_ms:.1f}ms")
    print(f"   Model: {result.model_used}")
    print(f"\n   Explanation:\n   {result.explanation[:200]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - Module 8 is working!")
print("=" * 60)
