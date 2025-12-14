from __future__ import annotations
import csv
import sys
from pathlib import Path
# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.predict import Predictor
from src.config import settings


def evaluate(sample_path: Path) -> dict:
    predictor = Predictor()
    predictor.load()
    top1_hits = 0
    mrr_sum = 0.0
    p_at_5_sum = 0.0
    r_at_5_sum = 0.0
    latencies = []
    n = 0

    with open(sample_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n += 1
            note = row["text"]
            gt_codes = eval(row["ground_truth_codes"]) if row.get("ground_truth_codes") else []
            out = predictor.predict(note, top_k=5)
            latencies.append(out.get("latency_ms", 0))
            preds = [p["icd10_code"] for p in out.get("predictions", [])]
            # Top-1
            if len(preds) > 0 and any(preds[0] == gt for gt in gt_codes):
                top1_hits += 1
            # MRR
            rr = 0.0
            for i, p in enumerate(preds, start=1):
                if p in gt_codes:
                    rr = 1.0 / i
                    break
            mrr_sum += rr
            # P@5 and R@5
            inter = len(set(preds).intersection(set(gt_codes)))
            p_at_5_sum += inter / max(1, len(preds))
            r_at_5_sum += inter / max(1, len(gt_codes))

    return {
        "samples": n,
        "top1": round(top1_hits / max(1, n), 4),
        "mrr": round(mrr_sum / max(1, n), 4),
        "p_at_5": round(p_at_5_sum / max(1, n), 4),
        "r_at_5": round(r_at_5_sum / max(1, n), 4),
        "latency_ms_avg": int(sum(latencies) / max(1, len(latencies))),
    }


def main():
    sample_path = settings.data_processed_dir / "sample_notes.csv"
    if not sample_path.exists():
        print(f"Missing {sample_path}. Please generate synthetic notes first.")
        return
    metrics = evaluate(sample_path)
    print(metrics)


if __name__ == "__main__":
    main()
