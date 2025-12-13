from __future__ import annotations
import json
import sys
from pathlib import Path
# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.icd10_kb import build_kb
from src.retrieval import BM25Retriever
from src.config import settings


def main():
    kb = build_kb()
    retriever = BM25Retriever()
    retriever.fit(kb)
    # Persist minimal index artifacts
    index_dir = settings.index_dir
    index_dir.mkdir(parents=True, exist_ok=True)
    docs_path = index_dir / "docs.json"
    docs = [(str(item.get("title", "")) + " | " + str(item.get("description", "")).strip()) for item in kb]
    codes = [item.get("icd10_code", "") for item in kb]
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump({"docs": docs, "codes": codes}, f, ensure_ascii=False)
    print(f"KB size: {len(kb)} | Saved: {docs_path}")


if __name__ == "__main__":
    main()
