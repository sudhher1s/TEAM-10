"""
Module 2: Embeddings Builder - Core Embeddings Builder
Loads KB from Module 1, generates semantic embeddings using sentence-transformers.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from .schemas import EmbeddingsMetadata, ItemMetadata, EmbeddingsStats


class EmbeddingsBuilder:
    """
    Loads KB from Module 1 and generates semantic embeddings.
    Uses SentenceTransformer with all-MiniLM-L6-v2 (384-dimensional vectors).
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 32,
        device: str = "cpu",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize embeddings builder.
        
        Args:
            model_name: HuggingFace model name for sentence-transformers
            batch_size: Number of items to embed at once
            device: "cpu" or "cuda" for GPU acceleration
            logger: Python logger instance
        """
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")
        
        self.model_name = model_name
        self.batch_size = batch_size
        self.device = device
        self.logger = logger or logging.getLogger(__name__)
        
        self.logger.info(f"Loading SentenceTransformer model: {model_name} on {device}")
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def load_kb_from_json(self, kb_json_path: Path) -> List[Dict[str, Any]]:
        """
        Load KB from Module 1's output (kb.json).
        
        Args:
            kb_json_path: Path to kb.json from Module 1
            
        Returns:
            List of KB items
        """
        with open(kb_json_path, 'r', encoding='utf-8') as f:
            kb_items = json.load(f)
        
        self.logger.info(f"Loaded KB with {len(kb_items)} items from {kb_json_path}")
        return kb_items
    
    def _prepare_text_for_embedding(self, item: Dict[str, Any]) -> str:
        """
        Prepare text from KB item for embedding.
        Combines title + description to capture full semantics.
        
        Args:
            item: KB item dictionary
            
        Returns:
            Text string for embedding
        """
        title = item.get('title', '')
        description = item.get('description', '')
        
        # Combine title and description, separated by space
        text = f"{title} {description}".strip()
        return text
    
    def build(self, kb_json_path: Path, output_dir: Path) -> EmbeddingsStats:
        """
        Build embeddings for all KB items.
        
        Args:
            kb_json_path: Path to kb.json from Module 1
            output_dir: Directory to save embeddings and metadata
            
        Returns:
            EmbeddingsStats with process statistics
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load KB
        kb_items = self.load_kb_from_json(kb_json_path)
        kb_version = "v1.0"  # Default version
        
        total_items = len(kb_items)
        self.logger.info(f"Starting embedding of {total_items} KB items...")
        
        # Prepare texts for embedding
        texts = []
        code_to_index = {}
        
        for idx, item in enumerate(kb_items):
            code = item.get('code')
            text = self._prepare_text_for_embedding(item)
            texts.append(text)
            code_to_index[code] = idx
        
        # Generate embeddings in batches
        start_time = time.time()
        self.logger.info(f"Embedding {total_items} items in batches of {self.batch_size}...")
        
        embeddings_list = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self.model.encode(
                batch_texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings_list.append(batch_embeddings)
            
            if (i // self.batch_size + 1) % 10 == 0:
                self.logger.info(f"  Embedded {min(i + self.batch_size, total_items)}/{total_items} items")
        
        # Concatenate all embeddings
        embeddings_matrix = np.concatenate(embeddings_list, axis=0)
        embedding_time = time.time() - start_time
        
        self.logger.info(f"Embeddings generated. Shape: {embeddings_matrix.shape} in {embedding_time:.2f}s")
        
        # Save embeddings as numpy array
        embeddings_path = output_dir / "embeddings.npy"
        np.save(embeddings_path, embeddings_matrix)
        self.logger.info(f"Saved embeddings to {embeddings_path}")
        
        # Build item metadata
        item_metadata_list = []
        for idx, item in enumerate(kb_items):
            metadata = ItemMetadata(
                embeddings_id=idx,
                code=item.get('code', ''),
                title=item.get('title', ''),
                description=item.get('description', '')[:200],  # Truncate description
                category=item.get('category', ''),
                embedding_dim=self.embedding_dim
            )
            item_metadata_list.append(metadata.to_dict())
        
        # Save item metadata
        metadata_path = output_dir / "item_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(item_metadata_list, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved item metadata to {metadata_path}")
        
        # Save embeddings metadata
        embeddings_metadata = EmbeddingsMetadata(
            model_name=self.model_name,
            embedding_dim=self.embedding_dim,
            num_embeddings=len(embeddings_matrix),
            num_kb_items=total_items,
            timestamp=datetime.now().isoformat(),
            kb_version=kb_version
        )
        
        metadata_config_path = output_dir / "metadata.json"
        with open(metadata_config_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings_metadata.to_dict(), f, indent=2)
        self.logger.info(f"Saved metadata config to {metadata_config_path}")
        
        # Save code-to-index mapping
        mapping_path = output_dir / "code_to_index.json"
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(code_to_index, f, indent=2)
        self.logger.info(f"Saved code-to-index mapping to {mapping_path}")
        
        # Calculate statistics
        stats = EmbeddingsStats(
            total_items=total_items,
            embedded_items=len(embeddings_matrix),
            failed_items=0,
            embedding_time_seconds=embedding_time,
            avg_time_per_item_ms=(embedding_time / total_items) * 1000,
            embedding_dim=self.embedding_dim,
            model_name=self.model_name
        )
        
        # Save statistics
        stats_path = output_dir / "stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats.to_dict(), f, indent=2)
        self.logger.info(f"Saved statistics to {stats_path}")
        
        self.logger.info("=" * 60)
        self.logger.info(f"[OK] Embeddings building complete!")
        self.logger.info(f"  - Total items: {stats.total_items}")
        self.logger.info(f"  - Embedded items: {stats.embedded_items}")
        self.logger.info(f"  - Embedding dimension: {stats.embedding_dim}")
        self.logger.info(f"  - Model: {stats.model_name}")
        self.logger.info(f"  - Time: {stats.embedding_time_seconds:.2f}s ({stats.avg_time_per_item_ms:.3f}ms per item)")
        self.logger.info("=" * 60)
        
        return stats
    
    def load_embeddings(self, embeddings_dir: Path) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, int]]:
        """
        Load previously saved embeddings.
        
        Args:
            embeddings_dir: Directory with saved embeddings
            
        Returns:
            Tuple of (embeddings_matrix, item_metadata_list, code_to_index)
        """
        embeddings = np.load(embeddings_dir / "embeddings.npy")
        
        with open(embeddings_dir / "item_metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        with open(embeddings_dir / "code_to_index.json", 'r', encoding='utf-8') as f:
            code_to_index = json.load(f)
        
        self.logger.info(f"Loaded embeddings: shape {embeddings.shape}")
        return embeddings, metadata, code_to_index
