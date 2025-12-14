import logging
from pathlib import Path
import sys

# Ensure workspace root is on sys.path for package imports
WORKSPACE_ROOT = Path(r"c:\MY PROJECTS\GEN AI")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from working_modules.module_4_query_encoder.src.query_encoder import QueryEncoder

logging.basicConfig(level=logging.INFO)

OUTPUT_DIR = Path(r"c:\MY PROJECTS\GEN AI\working_modules\output")
INDEX_PATH = OUTPUT_DIR / "faiss.index"
ITEM_META_PATH = OUTPUT_DIR / "item_metadata.json"


def test_query_encoder_basic():
    enc = QueryEncoder(index_path=INDEX_PATH, item_metadata_path=ITEM_META_PATH)
    res = enc.search("cholera", top_k=5)
    assert len(res.items) > 0
    assert res.elapsed_ms < 50


def test_query_encoder_cardiac():
    enc = QueryEncoder(index_path=INDEX_PATH, item_metadata_path=ITEM_META_PATH)
    res = enc.search("myocardial infarction", top_k=5)
    assert len(res.items) == 5
    codes = [it.code for it in res.items]
    assert any(code.startswith("I21") for code in codes)
