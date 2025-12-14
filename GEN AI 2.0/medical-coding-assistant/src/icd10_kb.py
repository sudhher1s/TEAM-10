from __future__ import annotations
from .data_loader import load_icd10, load_icd9to10


def build_kb() -> list[dict]:
    """Build unified ICD-10 KB list of dicts: {icd10_code, title, description, category}."""
    icd10_rows = load_icd10()
    icd9to10_rows = load_icd9to10()

    kb: list[dict] = []
    for r in icd10_rows:
        title = r.get("category") or r.get("icd10_code")
        description = (r.get("full_description") or r.get("alt_description") or "").strip()
        kb.append({
            "icd10_code": r.get("icd10_code", "").strip(),
            "title": title.strip() if isinstance(title, str) else str(title),
            "description": description,
            "category": (r.get("category") or "").strip(),
        })

    # Enrich description using ICD-9 mapping (prefer the longest description when available)
    if icd9to10_rows:
        desc_map: dict[str, str] = {}
        for m in icd9to10_rows:
            code = m.get("icd10_code", "").strip()
            desc = m.get("description", "").strip()
            if not code:
                continue
            if code not in desc_map or len(desc) > len(desc_map[code]):
                desc_map[code] = desc
        for item in kb:
            if not item["description"] and item["icd10_code"] in desc_map:
                item["description"] = desc_map[item["icd10_code"]]

    # Deduplicate by icd10_code
    seen = set()
    final_kb: list[dict] = []
    for item in kb:
        code = item["icd10_code"]
        if code and code not in seen:
            final_kb.append(item)
            seen.add(code)
    return final_kb
