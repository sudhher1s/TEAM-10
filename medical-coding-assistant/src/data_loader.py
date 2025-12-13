from pathlib import Path
import shutil
import csv
from .config import settings

ROOT = Path(__file__).resolve().parent.parent.parent


def ensure_raw_files_present() -> None:
    """Copy root-level raw files into data/raw if found; else expect they already exist."""
    src_icd10 = ROOT / "ICD10codes.csv"
    src_icd9to10 = ROOT / "icd9to10dictionary.txt"
    dst_icd10 = settings.data_raw_dir / settings.icd10_csv
    dst_icd9to10 = settings.data_raw_dir / settings.icd9to10_txt

    if src_icd10.exists() and not dst_icd10.exists():
        shutil.copy2(src_icd10, dst_icd10)
    if src_icd9to10.exists() and not dst_icd9to10.exists():
        shutil.copy2(src_icd9to10, dst_icd9to10)


def load_icd10() -> list[dict]:
    ensure_raw_files_present()
    path = settings.data_raw_dir / settings.icd10_csv
    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for r in reader:
            # Expect 6 columns: chapter_code, sub_code, icd10_code, full_description, alt_description, category
            if len(r) < 6:
                # pad missing
                r = r + [""] * (6 - len(r))
            rows.append({
                "chapter_code": r[0].strip(),
                "sub_code": r[1].strip(),
                "icd10_code": r[2].strip(),
                "full_description": r[3].strip(),
                "alt_description": r[4].strip(),
                "category": r[5].strip(),
            })
    return rows


def load_ic9to10_list(path: Path) -> list[dict]:
    items: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) < 3:
                continue
            items.append({
                "icd9_code": parts[0].strip(),
                "icd10_code": parts[1].strip(),
                "description": parts[2].strip(),
            })
    return items


def load_icd9to10() -> list[dict]:
    ensure_raw_files_present()
    path = settings.data_raw_dir / settings.icd9to10_txt
    if not path.exists():
        return []
    return load_ic9to10_list(path)
