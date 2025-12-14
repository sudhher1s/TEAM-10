from __future__ import annotations
import csv
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.predict import Predictor
from src.config import settings


def evaluate_tsv(path: Path, top_k: int = 5) -> dict:
    p = Predictor(); p.load()
    n = 0
    top1 = 0.0
    mrr = 0.0
    p5 = 0.0
    r5 = 0.0
    lat = []
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            n += 1
            note = row["text"]
            gt = eval(row["ground_truth_codes"]) if row.get("ground_truth_codes") else []
            out = p.predict(note, top_k=top_k)
            lat.append(out.get("latency_ms", 0))
            preds = [x.get("icd10_code") for x in out.get("predictions", [])]
            if preds and any(preds[0] == g for g in gt):
                top1 += 1
            rr = 0.0
            for i, code in enumerate(preds, start=1):
                if code in gt: rr = 1.0/i; break
            mrr += rr
            inter = len(set(preds).intersection(set(gt)))
            p5 += inter / max(1, len(preds))
            r5 += inter / max(1, len(gt))
    return {
        "samples": n,
        "top1": round(top1/max(1,n),4),
        "mrr": round(mrr/max(1,n),4),
        "p_at_5": round(p5/max(1,n),4),
        "r_at_5": round(r5/max(1,n),4),
        "latency_ms_avg": int(sum(lat)/max(1,len(lat)))
    }


def main():
    path = settings.data_processed_dir / "mimic_eval.tsv"
    if not path.exists():
        print(f"Missing {path}. Run 04_prepare_mimic.py first.")
        return
    print(evaluate_tsv(path))


if __name__ == "__main__":
    main()
