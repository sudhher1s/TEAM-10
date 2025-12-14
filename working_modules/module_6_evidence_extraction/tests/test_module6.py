import sys
from pathlib import Path

# Add workspace root for imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_4_query_encoder.src.query_encoder import QueryEncoder
from working_modules.module_5_reranker.src.reranker import Reranker
from working_modules.module_6_evidence_extraction.src.evidence_extractor import EvidenceExtractor

OUTPUT_DIR = Path(r"c:\MY PROJECTS\GEN AI\working_modules\output")
KB_PATH = Path(r"c:\MY PROJECTS\GEN AI\working_modules\module_1_data_kb\output\kb.json")
INDEX_PATH = OUTPUT_DIR / "faiss.index"
ITEM_META_PATH = OUTPUT_DIR / "item_metadata.json"


def test_evidence_extraction_basic():
    """Test basic evidence extraction for cholera codes."""
    extractor = EvidenceExtractor(KB_PATH)
    
    # Simple candidates
    candidates = [{"code": "A000"}, {"code": "A001"}, {"code": "A009"}]
    evidence_set = extractor.extract("cholera", candidates)
    
    assert len(evidence_set.items) == 3
    assert evidence_set.items[0].code == "A000"
    assert "cholera" in evidence_set.items[0].title.lower()
    assert evidence_set.items[0].description is not None
    assert isinstance(evidence_set.items[0].aliases, list)


def test_evidence_extraction_with_reranker():
    """Test full M4 -> M5 -> M6 pipeline."""
    # M4: Retrieve
    encoder = QueryEncoder(index_path=INDEX_PATH, item_metadata_path=ITEM_META_PATH)
    res = encoder.search("myocardial infarction", top_k=50)
    candidates = [
        {"code": it.code, "title": it.title, "category": it.category, "index_id": it.index_id}
        for it in res.items
    ]
    
    # M5: Rerank
    reranker = Reranker()
    rres = reranker.rerank(res.query, candidates, top_k=10)
    
    # M6: Extract evidence
    extractor = EvidenceExtractor(KB_PATH)
    evidence_set = extractor.extract(
        res.query,
        [{"code": it.code, "score": it.score} for it in rres.items],
    )
    
    assert len(evidence_set.items) == 10
    # Check that cardiac codes are present
    codes = [ev.code for ev in evidence_set.items]
    assert any(code.startswith("I21") for code in codes)
    # Verify descriptions and aliases are populated
    assert all(ev.description for ev in evidence_set.items)
