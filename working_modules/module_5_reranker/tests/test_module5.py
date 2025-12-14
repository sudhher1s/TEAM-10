import sys
from pathlib import Path

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_4_query_encoder.src.query_encoder import QueryEncoder
from working_modules.module_5_reranker.src.reranker import Reranker

OUTPUT_DIR = Path(r"c:\MY PROJECTS\GEN AI\working_modules\output")
INDEX_PATH = OUTPUT_DIR / "faiss.index"
ITEM_META_PATH = OUTPUT_DIR / "item_metadata.json"


def test_reranker_end_to_end():
    enc = QueryEncoder(index_path=INDEX_PATH, item_metadata_path=ITEM_META_PATH)
    res = enc.search("cholera", top_k=30)
    candidates = [
        {"code": it.code, "title": it.title, "category": it.category, "index_id": it.index_id}
        for it in res.items
    ]
    rr = Reranker()
    rres = rr.rerank(res.query, candidates, top_k=10)
    assert len(rres.items) == 10
    # Ensure family codes are present at top positions after reranking
    codes = [it.code for it in rres.items]
    assert any(code.startswith("A00") for code in codes)
