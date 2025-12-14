"""
Module 2: Quick Smoke Test - Test with 100 items only
"""

import sys
import logging
from pathlib import Path
import json
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MODULE_DIR = SCRIPT_DIR.parent
MODULE_1_OUTPUT = Path("c:/MY PROJECTS/GEN AI/working_modules/module_1_data_kb/output")
MODULE_2_OUTPUT = MODULE_DIR / "output_test"

# Import module
sys.path.insert(0, str(SCRIPT_DIR))
from src.embeddings_builder import EmbeddingsBuilder


def test_quick():
    """Quick test with just 100 items."""
    logger.info("=" * 60)
    logger.info("QUICK TEST: 100 items only")
    logger.info("=" * 60)
    
    # Load KB
    kb_path = MODULE_1_OUTPUT / "kb.json"
    with open(kb_path, 'r') as f:
        all_items = json.load(f)
    
    # Take first 100 items
    test_items = all_items[:100]
    logger.info(f"Using {len(test_items)} items for quick test")
    
    # Save subset
    subset_path = SCRIPT_DIR / "kb_subset.json"
    with open(subset_path, 'w') as f:
        json.dump(test_items, f)
    logger.info(f"Saved subset to {subset_path}")
    
    # Initialize builder
    builder = EmbeddingsBuilder(
        model_name="all-MiniLM-L6-v2",
        batch_size=32,
        device="cpu",
        logger=logger
    )
    logger.info(f"[OK] Model loaded (dimension: {builder.embedding_dim})")
    
    # Build embeddings
    MODULE_2_OUTPUT.mkdir(parents=True, exist_ok=True)
    stats = builder.build(subset_path, MODULE_2_OUTPUT)
    
    logger.info("=" * 60)
    logger.info(f"[OK] QUICK TEST COMPLETE!")
    logger.info(f"  - Embedded {stats.embedded_items} items")
    logger.info(f"  - Time: {stats.embedding_time_seconds:.2f}s")
    logger.info(f"  - Dimension: {stats.embedding_dim}")
    logger.info("=" * 60)
    
    # Verify embeddings
    embeddings = np.load(MODULE_2_OUTPUT / "embeddings.npy")
    logger.info(f"[OK] Embeddings shape: {embeddings.shape}")
    logger.info(f"  - Min: {embeddings.min():.4f}, Max: {embeddings.max():.4f}")
    logger.info(f"  - Mean: {embeddings.mean():.4f}, Std: {embeddings.std():.4f}")
    
    # Check metadata
    with open(MODULE_2_OUTPUT / "item_metadata.json", 'r') as f:
        metadata = json.load(f)
    logger.info(f"[OK] Metadata: {len(metadata)} items")
    logger.info(f"  - First: {metadata[0]['code']} - {metadata[0]['title']}")
    logger.info(f"  - Last: {metadata[-1]['code']} - {metadata[-1]['title']}")
    
    logger.info("\n" + "=" * 60)
    logger.info("[SUCCESS] All quick tests passed!")
    logger.info("To run full test (71,704 items), use: test_module2.py")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_quick()
