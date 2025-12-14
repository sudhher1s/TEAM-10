"""
Module 3: Vector Index - Test Suite
"""

import sys
import logging
from pathlib import Path
import json
import time
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
MODULE_2_OUTPUT = Path("c:/MY PROJECTS/GEN AI/working_modules/output")
MODULE_3_OUTPUT = MODULE_DIR / "output"

# Import module
sys.path.insert(0, str(SCRIPT_DIR))
from src.vector_index_builder import VectorIndexBuilder


def test_vector_index():
    """Test VectorIndexBuilder with Module 2 embeddings."""
    
    logger.info("=" * 60)
    logger.info("Test 1: VectorIndexBuilder Initialization")
    logger.info("=" * 60)
    
    try:
        builder = VectorIndexBuilder(
            index_type="IVF",
            nlist=100,
            num_probes=10,
            metric="L2",
            logger=logger
        )
        logger.info(f"[OK] VectorIndexBuilder initialized")
        logger.info(f"  - Index type: IVF")
        logger.info(f"  - Number of clusters: 100")
        logger.info(f"  - Number of probes: 10")
    except Exception as e:
        logger.error(f"[FAILED] Initialization: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Load Embeddings from Module 2")
    logger.info("=" * 60)
    
    embeddings_path = MODULE_2_OUTPUT / "embeddings.npy"
    metadata_path = MODULE_2_OUTPUT / "item_metadata.json"
    
    if not embeddings_path.exists():
        logger.error(f"[FAILED] Embeddings not found: {embeddings_path}")
        return False
    
    try:
        embeddings, metadata = builder.load_embeddings(embeddings_path, metadata_path)
        logger.info(f"[OK] Embeddings loaded")
        logger.info(f"  - Shape: {embeddings.shape}")
        logger.info(f"  - Metadata items: {len(metadata)}")
        logger.info(f"  - Data type: {embeddings.dtype}")
    except Exception as e:
        logger.error(f"[FAILED] Loading embeddings: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Build FAISS Index")
    logger.info("=" * 60)
    
    try:
        index, stats = builder.build(
            embeddings_path,
            metadata_path,
            model_name="all-MiniLM-L6-v2",
            kb_version="v1.0"
        )
        logger.info(f"[OK] Index built successfully")
        logger.info(f"  - Index type: {stats.index_type}")
        logger.info(f"  - Vectors indexed: {stats.num_vectors:,}")
        logger.info(f"  - Build time: {stats.build_time_seconds:.2f}s")
        logger.info(f"  - Speed: {stats.vectors_per_second:.0f} vectors/sec")
    except Exception as e:
        logger.error(f"[FAILED] Building index: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Save Index")
    logger.info("=" * 60)
    
    try:
        MODULE_3_OUTPUT.mkdir(parents=True, exist_ok=True)
        builder.save_index(MODULE_3_OUTPUT)
        logger.info(f"[OK] Index saved to {MODULE_3_OUTPUT}")
    except Exception as e:
        logger.error(f"[FAILED] Saving index: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 5: Verify Output Files")
    logger.info("=" * 60)
    
    required_files = [
        "faiss.index",
        "index_metadata.json",
        "code_to_index.json"
    ]
    
    all_exist = True
    for fname in required_files:
        fpath = MODULE_3_OUTPUT / fname
        if fpath.exists():
            size = fpath.stat().st_size
            logger.info(f"  [OK] {fname} ({size:,} bytes)")
        else:
            logger.error(f"  [FAILED] {fname} not found")
            all_exist = False
    
    if not all_exist:
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 6: Search Test (Cholera)")
    logger.info("=" * 60)
    
    try:
        # Get embedding for A000 (cholera)
        embeddings = np.load(embeddings_path)
        a000_embedding = embeddings[0]
        
        # Search for similar codes
        results = builder.search(a000_embedding, top_k=5)
        
        logger.info(f"[OK] Search completed in {results.search_time_ms:.2f}ms")
        logger.info(f"  Top-5 similar codes to A000 (cholera):")
        for i, result in enumerate(results.results, 1):
            logger.info(f"    {i}. {result.code}: {result.title[:50]}")
            logger.info(f"       Similarity: {result.similarity_score:.4f}")
    except Exception as e:
        logger.error(f"[FAILED] Search: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 7: Search Test (Cardiac)")
    logger.info("=" * 60)
    
    try:
        # Find a cardiac code (I21.01 or similar)
        with open(MODULE_2_OUTPUT / "code_to_index.json") as f:
            code_to_idx = json.load(f)
        
        if "I2101" in code_to_idx:
            cardiac_idx = code_to_idx["I2101"]
            cardiac_embedding = embeddings[cardiac_idx]
            
            results = builder.search(cardiac_embedding, top_k=5)
            
            logger.info(f"[OK] Search completed in {results.search_time_ms:.2f}ms")
            logger.info(f"  Top-5 similar codes to I2101 (MI):")
            for i, result in enumerate(results.results, 1):
                logger.info(f"    {i}. {result.code}: {result.title[:50]}")
                logger.info(f"       Similarity: {result.similarity_score:.4f}")
        else:
            logger.info("  [SKIP] I2101 not found in KB")
    except Exception as e:
        logger.error(f"[FAILED] Cardiac search: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Test 8: Load Index from Disk")
    logger.info("=" * 60)
    
    try:
        builder2 = VectorIndexBuilder(logger=logger)
        builder2.load_index(MODULE_3_OUTPUT)
        logger.info(f"[OK] Index loaded from disk")
        logger.info(f"  - Vectors in index: {builder2.index.ntotal:,}")
    except Exception as e:
        logger.error(f"[FAILED] Loading index: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("[OK] All tests passed!")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    success = test_vector_index()
    sys.exit(0 if success else 1)
