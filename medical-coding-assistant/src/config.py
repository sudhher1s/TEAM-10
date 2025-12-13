import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Settings:
    data_raw_dir: Path = Path(__file__).resolve().parent.parent / "data" / "raw"
    data_processed_dir: Path = Path(__file__).resolve().parent.parent / "data" / "processed"
    index_dir: Path = Path(__file__).resolve().parent.parent / "data" / "index"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Filenames
    icd10_csv: str = "ICD10codes.csv"
    icd9to10_txt: str = "icd9to10dictionary.txt"

    # Lightweight tuning parameters
    rerank_overlap_weight: float = 0.05  # weight per overlapping token
    title_weight_factor: int = 2  # how many times to repeat title tokens in retriever

settings = Settings()

# Ensure directories exist
settings.data_raw_dir.mkdir(parents=True, exist_ok=True)
settings.data_processed_dir.mkdir(parents=True, exist_ok=True)
settings.index_dir.mkdir(parents=True, exist_ok=True)
