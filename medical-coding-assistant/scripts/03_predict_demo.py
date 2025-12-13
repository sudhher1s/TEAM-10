from __future__ import annotations
import json
import sys
from pathlib import Path
# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.predict import Predictor


def main():
    predictor = Predictor()
    predictor.load()
    note = "Patient with chest pain, SOB, EKG ST elevation"
    out = predictor.predict(note, top_k=5)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
