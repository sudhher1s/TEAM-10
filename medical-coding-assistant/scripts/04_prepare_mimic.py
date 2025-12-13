from __future__ import annotations
import csv
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import settings
from src.data_loader import load_icd9to10


def load_icd9_to_icd10_map() -> dict[str, list[str]]:
    mapping = load_icd9to10()
    out: dict[str, list[str]] = {}
    for m in mapping:
        icd9 = str(m.get("icd9_code", "")).strip()
        icd10 = str(m.get("icd10_code", "")).strip()
        if icd9 and icd10:
            out.setdefault(icd9, []).append(icd10)
    return out
def normalize_icd9(code: str) -> list[str]:
    code = code.strip()
    if not code:
        return []
    forms = {code}
    # add dotted form after 3 characters if not already dotted
    if "." not in code and len(code) > 3:
        forms.add(code[:3] + "." + code[3:])
    return list(forms)



def build_mimic_eval(mimic_dir: Path, out_path: Path, max_rows: int | None = 2000) -> int:
    # 1) Load ICD9 -> ICD10 map
    m = load_icd9_to_icd10_map()

    # 2) Read diagnoses per hadm_id from DIAGNOSES_ICD.csv
    diag_path = mimic_dir / "DIAGNOSES_ICD.csv"
    hadm_to_icd10: dict[str, set[str]] = {}
    hadm_to_icd9: dict[str, list[str]] = {}
    with diag_path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            hadm = row.get("HADM_ID") or row.get("hadm_id")
            icd9 = (row.get("ICD9_CODE") or row.get("icd9_code") or "").strip()
            if not hadm or not icd9:
                continue
            mapped = []
            for key in normalize_icd9(icd9):
                mapped.extend(m.get(key, []))
            if not mapped:
                continue
            hadm_to_icd10.setdefault(hadm, set()).update(mapped)
            hadm_to_icd9.setdefault(hadm, []).append(icd9)

    # 3) Read discharge summaries from NOTEEVENTS.csv
    notes_path = mimic_dir / "NOTEEVENTS.csv"
    hadm_to_note: dict[str, str] = {}
    with notes_path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            cat = (row.get("CATEGORY") or row.get("category") or "").lower()
            if "discharge" not in cat:
                continue
            hadm = row.get("HADM_ID") or row.get("hadm_id")
            text = row.get("TEXT") or row.get("text") or ""
            if not hadm or not text:
                continue
            # keep the longest note per hadm
            if len(text) > len(hadm_to_note.get(hadm, "")):
                hadm_to_note[hadm] = text

    # 3b) Fallback pseudo-notes from D_ICD_DIAGNOSES when notes are missing
    dict_diag = mimic_dir / "D_ICD_DIAGNOSES.csv"
    icd9_to_long: dict[str, str] = {}
    if dict_diag.exists():
        with dict_diag.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                code = (row.get("icd9_code") or row.get("ICD9_CODE") or "").strip()
                long_t = (row.get("long_title") or row.get("LONG_TITLE") or row.get("short_title") or "").strip()
                if code and long_t:
                    icd9_to_long[code] = long_t

    # 4) Join and write TSV
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["note_id", "hadm_id", "text", "ground_truth_codes"])
        for i, (hadm, codes) in enumerate(hadm_to_icd10.items(), start=1):
            if hadm in hadm_to_note:
                text = hadm_to_note[hadm]
            else:
                # synthesize a pseudo-note from ICD-9 long titles (fallback for demo data with empty NOTEEVENTS)
                icd9_list = hadm_to_icd9.get(hadm, [])
                titles = []
                for c in icd9_list:
                    # try both raw and dotted forms
                    found = icd9_to_long.get(c)
                    if not found and "." not in c and len(c) > 3:
                        found = icd9_to_long.get(c[:3]+"."+c[3:])
                    if found:
                        titles.append(found)
                if not titles:
                    continue
                text = "; ".join(titles)
            # simple filter: ensure text has at least 10 words
            if len(text.split()) < 10:
                continue
            w.writerow([i, hadm, text.replace("\t", " ").strip(), list(sorted(codes))])
            written += 1
            if max_rows and written >= max_rows:
                break
    return written


def main():
    # Default MIMIC demo folder at repo root
    mimic_dir = Path(__file__).resolve().parents[2] / "mimic-iii-clinical-database-demo-1.4"
    out_path = settings.data_processed_dir / "mimic_eval.tsv"
    if not mimic_dir.exists():
        print(f"MIMIC demo folder not found at {mimic_dir}")
        return
    n = build_mimic_eval(mimic_dir, out_path)
    print(f"Wrote {n} rows to {out_path}")


if __name__ == "__main__":
    main()
