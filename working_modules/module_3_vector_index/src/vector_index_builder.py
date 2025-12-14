"""
Module 3: Vector Index Builder - Core Implementation
Builds FAISS index for ultra-fast nearest-neighbor similarity search.
"""

import json
import logging
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

from .schemas import IndexMetadata, SearchResult, SearchResults, IndexStats


class VectorIndexBuilder:
    """
    Builds and manages FAISS indices for fast vector similarity search.
    Supports IVF (Inverted File Index) for scalable search over 71K+ vectors.
    """
    
    def __init__(
        self,
        index_type: str = "IVF",
        nlist: int = 100,
        num_probes: int = 10,
        metric: str = "L2",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize index builder.
        
        Args:
            index_type: "IVF" (Inverted File) or "FLAT" (exhaustive search)
            nlist: Number of clusters for IVF (100-200 typical)
            num_probes: Number of clusters to search (1-20; higher = slower but more accurate)
            metric: "L2" (Euclidean) or "IP" (Inner Product)
            logger: Python logger
        """
        if faiss is None:
            raise ImportError("faiss not installed. Run: pip install faiss-cpu")
        
        self.index_type = index_type
        self.nlist = nlist
        self.num_probes = num_probes
        self.metric = metric
        self.logger = logger or logging.getLogger(__name__)
        
        self.index = None
        self.metadata = None
        self.item_metadata = None
        self.code_to_index = None
        
        self.logger.info(f"VectorIndexBuilder initialized (type={index_type}, nlist={nlist}, num_probes={num_probes})")
    
    def load_embeddings(self, embeddings_path: Path, metadata_path: Path) -> Tuple[np.ndarray, List[Dict]]:
        """
        Load embeddings from Module 2.
        
        Args:
            embeddings_path: Path to embeddings.npy
            metadata_path: Path to item_metadata.json
            
        Returns:
            (embeddings_matrix, item_metadata_list)
        """
        self.logger.info(f"Loading embeddings from {embeddings_path}")
        embeddings = np.load(embeddings_path)
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.logger.info(f"Loaded embeddings: shape {embeddings.shape}, metadata: {len(metadata)} items")
        return embeddings, metadata
    
    def build(
        self,
        embeddings_path: Path,
        metadata_path: Path,
        model_name: str = "all-MiniLM-L6-v2",
        kb_version: str = "v1.0"
    ) -> Tuple[faiss.Index, IndexStats]:
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings_path: Path to embeddings.npy from Module 2
            metadata_path: Path to item_metadata.json
            model_name: Name of embedding model
            kb_version: KB version identifier
            
        Returns:
            (faiss_index, stats)
        """
        # Load embeddings and metadata
        embeddings, self.item_metadata = self.load_embeddings(embeddings_path, metadata_path)
        
        num_vectors = embeddings.shape[0]
        embedding_dim = embeddings.shape[1]
        
        self.logger.info(f"Building {self.index_type} index with {num_vectors} vectors ({embedding_dim} dims)")
        
        start_time = time.time()
        
        # Convert to float32 (required by FAISS)
        embeddings = embeddings.astype(np.float32)
        
        # Build index based on type
        if self.index_type == "IVF":
            self._build_ivf_index(embeddings, embedding_dim, num_vectors)
        elif self.index_type == "FLAT":
            self._build_flat_index(embeddings, embedding_dim)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")
        
        build_time = time.time() - start_time
        
        self.logger.info(f"Index built in {build_time:.2f}s ({num_vectors/build_time:.0f} vectors/sec)")
        
        # Create metadata
        self.metadata = IndexMetadata(
            index_type=self.index_type,
            embedding_dim=embedding_dim,
            num_vectors=num_vectors,
            num_probes=self.num_probes,
            nlist=self.nlist,
            metric=self.metric,
            model_name=model_name,
            kb_version=kb_version,
            timestamp=time.time(),
            embeddings_path=str(embeddings_path),
            metadata_path=str(metadata_path)
        )
        
        # Create code-to-index mapping
        self.code_to_index = {}
        for meta in self.item_metadata:
            self.code_to_index[meta['code']] = meta['embeddings_id']
        
        stats = IndexStats(
            num_vectors=num_vectors,
            embedding_dim=embedding_dim,
            index_type=self.index_type,
            build_time_seconds=build_time,
            index_size_bytes=0,  # FAISS doesn't expose this easily
            index_size_mb=0,
            vectors_per_second=num_vectors / build_time
        )
        
        return self.index, stats
    
    def _build_flat_index(self, embeddings: np.ndarray, embedding_dim: int):
        """Build exhaustive search index (FLAT)."""
        self.logger.info("Building FLAT index (exhaustive search)...")
        
        if self.metric == "L2":
            self.index = faiss.IndexFlatL2(embedding_dim)
        elif self.metric == "IP":
            self.index = faiss.IndexFlatIP(embedding_dim)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
        
        self.index.add(embeddings)
        self.logger.info(f"FLAT index built: {self.index.ntotal} vectors indexed")
    
    def _build_ivf_index(self, embeddings: np.ndarray, embedding_dim: int, num_vectors: int):
        """Build Inverted File (IVF) index for approximate nearest neighbor search."""
        self.logger.info(f"Building IVF index with {self.nlist} clusters...")
        
        # Quantizer: coarse level clustering
        if self.metric == "L2":
            quantizer = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, self.nlist, faiss.METRIC_L2)
        elif self.metric == "IP":
            quantizer = faiss.IndexFlatIP(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, self.nlist, faiss.METRIC_INNER_PRODUCT)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
        
        # Train index on a sample of data
        self.logger.info(f"Training on sample ({min(100000, num_vectors)} vectors)...")
        sample_size = min(100000, num_vectors)
        sample_indices = np.random.choice(num_vectors, sample_size, replace=False)
        sample = embeddings[sample_indices]
        
        self.index.train(sample)
        self.logger.info("Training complete")
        
        # Add all vectors
        self.logger.info(f"Adding {num_vectors} vectors to index...")
        self.index.add(embeddings)
        
        # Set search parameters
        self.index.nprobe = self.num_probes
        
        self.logger.info(f"IVF index built: {self.index.ntotal} vectors in {self.nlist} clusters, nprobe={self.num_probes}")
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> SearchResults:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Single query vector (384-dim)
            top_k: Number of results to return
            
        Returns:
            SearchResults with top-K matches
        """
        if self.index is None:
            raise RuntimeError("Index not built. Call build() first.")
        
        query_vector = query_vector.astype(np.float32).reshape(1, -1)
        
        start_time = time.time()
        distances, indices = self.index.search(query_vector, top_k)
        search_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Convert distances to similarity scores
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # Invalid result
                continue
            
            # Convert distance to similarity (depends on metric)
            if self.metric == "L2":
                # L2 distance: smaller = more similar
                # Convert to similarity score 0-1
                similarity = 1.0 / (1.0 + dist)
            else:  # IP
                # Inner product: larger = more similar
                similarity = float(dist)
            
            meta = self.item_metadata[idx]
            
            result = SearchResult(
                code=meta['code'],
                title=meta['title'],
                category=meta['category'],
                description=meta['description'][:200],
                similarity_score=float(similarity),
                embeddings_id=idx
            )
            results.append(result)
        
        return SearchResults(
            query="(vector query)",
            top_k=top_k,
            results=results,
            search_time_ms=search_time
        )
    
    def save_index(self, output_dir: Path):
        """Save index to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = output_dir / "faiss.index"
        faiss.write_index(self.index, str(index_path))
        self.logger.info(f"Saved FAISS index to {index_path}")
        
        # Save metadata
        metadata_path = output_dir / "index_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata.to_dict(), f, indent=2)
        self.logger.info(f"Saved index metadata to {metadata_path}")
        
        # Save code-to-index mapping
        mapping_path = output_dir / "code_to_index.json"
        with open(mapping_path, 'w') as f:
            json.dump(self.code_to_index, f, indent=2)
        self.logger.info(f"Saved code-to-index mapping to {mapping_path}")
    
    def load_index(self, output_dir: Path):
        """Load index from disk."""
        index_path = output_dir / "faiss.index"
        self.index = faiss.read_index(str(index_path))
        self.logger.info(f"Loaded FAISS index from {index_path}")
        
        metadata_path = output_dir / "index_metadata.json"
        with open(metadata_path, 'r') as f:
            meta_dict = json.load(f)
        self.metadata = IndexMetadata.from_dict(meta_dict)
        self.logger.info(f"Loaded index metadata from {metadata_path}")
        
        mapping_path = output_dir / "code_to_index.json"
        with open(mapping_path, 'r') as f:
            self.code_to_index = json.load(f)
        self.logger.info(f"Loaded code-to-index mapping from {mapping_path}")
