import sys
from pathlib import Path

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import google.generativeai as genai
import os

# List available models
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Available Gemini models:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
        print(f"  Display: {model.display_name}")
        print(f"  Description: {model.description[:100]}...")
        print()
