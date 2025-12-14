import sys
from pathlib import Path

# Ensure workspace root in sys.path
WORKSPACE = Path("c:/MY PROJECTS/GEN AI")
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "working_modules.module_10_api.src.api:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
