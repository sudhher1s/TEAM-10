import argparse
import sys
from pathlib import Path

# Ensure workspace root on sys.path for absolute imports
WORKSPACE = Path("c:/MY PROJECTS/GEN AI")
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from working_modules.module_9_orchestrator.src.orchestrator import MedicalCodingOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Run Module 9 Orchestrator end-to-end")
    parser.add_argument("--query", required=True, help="User query text")
    parser.add_argument("--index", required=True, help="Path to FAISS index (Module 3)")
    parser.add_argument("--metadata", required=True, help="Path to item_metadata.json (Module 2)")
    parser.add_argument("--kb", required=True, help="Path to kb.json (Module 6)")
    parser.add_argument("--provider", default="mock", choices=["openai", "mock"], help="LLM provider")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model name (if provider=openai)")
    parser.add_argument("--retrieve_k", type=int, default=100)
    parser.add_argument("--rerank_k", type=int, default=10)
    args = parser.parse_args()

    orchestrator = MedicalCodingOrchestrator(
        index_path=Path(args.index),
        item_metadata_path=Path(args.metadata),
        kb_path=Path(args.kb),
        llm_model=args.model,
        llm_provider=args.provider,
    )

    result = orchestrator.run(
        query=args.query,
        retrieve_k=args.retrieve_k,
        rerank_k=args.rerank_k,
    )

    # Minimal pretty print
    print("=== Module 9 Orchestrator Result ===")
    print({
        "query": result["query"],
        "top_evidence_codes": [ev["code"] for ev in result["evidence"]["items"][:5]],
        "llm_model": result["grounded"]["model"],
        "llm_confidence": result["grounded"]["confidence"],
        "is_safe": result["grounded"]["is_safe"],
        "warnings": result["grounded"]["warnings"],
    })


if __name__ == "__main__":
    main()
