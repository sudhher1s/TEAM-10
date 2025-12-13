from __future__ import annotations
from typing import List


def extract_spans(note_text: str, keywords: List[str]) -> List[str]:
    """Return verbatim substrings from note_text that match given keywords (case-insensitive).
    Ensures substrings are exact slices from original text.
    """
    note_lower = note_text.lower()
    spans: List[str] = []
    for kw in keywords:
        kw_l = kw.lower()
        idx = note_lower.find(kw_l)
        if idx != -1:
            spans.append(note_text[idx: idx + len(kw)])
    # Deduplicate while preserving order
    seen = set()
    out = []
    for s in spans:
        if s.lower() not in seen:
            out.append(s)
            seen.add(s.lower())
    return out
