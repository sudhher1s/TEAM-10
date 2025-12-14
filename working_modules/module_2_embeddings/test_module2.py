"""
Module 2: Embeddings Builder - Test Suite
"""

import sys
import logging
from pathlib import Path
import json
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MODULE_DIR = SCRIPT_DIR.parent
MODULE_1_OUTPUT = Path("c:/MY PROJECTS/GEN AI/working_modules/module_1_data_kb/output")
MODULE_2_OUTPUT = MODULE_DIR / "output"

# Import module
sys.path.insert(0, str(SCRIPT_DIR))
from src.embeddings_builder import EmbeddingsBuilder


def test_embeddings_builder():
    """Test EmbeddingsBuilder with Module 1 KB."""
    logger.info("=" * 60)
    logger.info("Test 1: EmbeddingsBuilder Initialization")
    logger.info("=" * 60)
    
    try:
        builder = EmbeddingsBuilder(
            model_name="all-MiniLM-L6-v2",
            batch_size=32,
            device="cpu",
            logger=logger
        )
        logger.info(f"[OK] EmbeddingsBuilder initialized")
        logger.info(f"  - Model: {builder.model_name}")
        logger.info(f"  - Embedding dimension: {builder.embedding_dim}")
        logger.info(f"  - Device: {builder.device}")
    except Exception as e:
        logger.error(f"[FAILED] EmbeddingsBuilder initialization: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Load KB from Module 1")
    logger.info("=" * 60)
    
    kb_path = MODULE_1_OUTPUT / "kb.json"
    if not kb_path.exists():
        logger.error(f"[FAILED] KB path not found: {kb_path}")
        return False
    
    try:
        kb_items = builder.load_kb_from_json(kb_path)
        logger.info(f"[OK] KB loaded")
        logger.info(f"  - Total items: {len(kb_items)}")
        if kb_items:
            logger.info(f"  - First item: {kb_items[0].get('code')} - {kb_items[0].get('title')}")
            logger.info(f"  - Last item: {kb_items[-1].get('code')} - {kb_items[-1].get('title')}")
    except Exception as e:
        logger.error(f"[FAILED] KB loading: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Build Embeddings (Full KB)")
    logger.info("=" * 60)
    
    try:
        MODULE_2_OUTPUT.mkdir(parents=True, exist_ok=True)
        stats = builder.build(kb_path, MODULE_2_OUTPUT)
        logger.info(f"[OK] Embeddings built successfully")
    except Exception as e:
        logger.error(f"[FAILED] Building embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Verify Output Files")
    logger.info("=" * 60)
    
    required_files = [
        "embeddings.npy",
        "item_metadata.json",
        "code_to_index.json",
        "metadata.json",
        "stats.json"
    ]
    
    all_exist = True
    for fname in required_files:
        fpath = MODULE_2_OUTPUT / fname
        if fpath.exists():
            size = fpath.stat().st_size
            logger.info(f"  [OK] {fname} ({size:,} bytes)")
        else:
            logger.error(f"  [FAILED] {fname} not found")
            all_exist = False
    
    if not all_exist:
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 5: Load and Verify Embeddings")
    logger.info("=" * 60)
    
    try:
        embeddings = np.load(MODULE_2_OUTPUT / "embeddings.npy")
        logger.info(f"[OK] Embeddings loaded")
        logger.info(f"  - Shape: {embeddings.shape}")
        logger.info(f"  - Data type: {embeddings.dtype}")
        logger.info(f"  - Min: {embeddings.min():.4f}, Max: {embeddings.max():.4f}")
        logger.info(f"  - Mean: {embeddings.mean():.4f}, Std: {embeddings.std():.4f}")
    except Exception as e:
        logger.error(f"[FAILED] Loading embeddings: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 6: Load and Verify Metadata")
    logger.info("=" * 60)
    
    try:
        with open(MODULE_2_OUTPUT / "item_metadata.json", 'r') as f:
            metadata = json.load(f)
        
        logger.info(f"[OK] Item metadata loaded")
        logger.info(f"  - Number of items: {len(metadata)}")
        
        if metadata:
            first_item = metadata[0]
            logger.info(f"  - First item: {first_item['code']} - {first_item['title']}")
            logger.info(f"    Category: {first_item['category']}")
            
            last_item = metadata[-1]
            logger.info(f"  - Last item: {last_item['code']} - {last_item['title']}")
    except Exception as e:
        logger.error(f"[FAILED] Loading metadata: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 7: Load and Verify Code-to-Index Mapping")
    logger.info("=" * 60)
    
    try:
        with open(MODULE_2_OUTPUT / "code_to_index.json", 'r') as f:
            mapping = json.load(f)
        
        logger.info(f"[OK] Code-to-index mapping loaded")
        logger.info(f"  - Number of codes: {len(mapping)}")
        logger.info(f"  - Sample mappings:")
        for code in list(mapping.keys())[:3]:
            idx = mapping[code]
            logger.info(f"    {code} -> {idx}")
    except Exception as e:
        logger.error(f"[FAILED] Loading mapping: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 8: Verify Embedding Statistics")
    logger.info("=" * 60)
    
    try:
        with open(MODULE_2_OUTPUT / "stats.json", 'r') as f:
            stats_data = json.load(f)
        
        logger.info(f"[OK] Statistics loaded")
        logger.info(f"  - Total items: {stats_data['total_items']}")
        logger.info(f"  - Embedded items: {stats_data['embedded_items']}")
        logger.info(f"  - Embedding dimension: {stats_data['embedding_dim']}")
        logger.info(f"  - Model: {stats_data['model_name']}")
        logger.info(f"  - Time: {stats_data['embedding_time_seconds']:.2f}s")
        logger.info(f"  - Avg time per item: {stats_data['avg_time_per_item_ms']:.3f}ms")
    except Exception as e:
        logger.error(f"[FAILED] Loading statistics: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("[OK] All tests passed!")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    success = test_embeddings_builder()
    sys.exit(0 if success else 1)
