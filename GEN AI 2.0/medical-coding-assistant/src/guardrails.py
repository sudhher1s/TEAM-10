from __future__ import annotations
import re
from typing import List

PHI_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN-like
    re.compile(r"\b\d{10}\b"),  # phone-like
    re.compile(r"\bMRN[:#]?\s*\d+\b", re.IGNORECASE),
]


def is_safe_note(note_text: str) -> tuple[bool, str]:
    # Allow shorter notes to reduce friction; still require minimal content.
    if len(note_text.split()) < 5:
        return False, "Note too short (<5 words)"
    for pat in PHI_PATTERNS:
        if pat.search(note_text):
            return False, "Potential PHI detected"
    return True, "OK"


def disclaimer() -> str:
    return "Not medical advice. Coding assistance only."


def constrain_to_kb(predictions: List[dict], kb_codes: set[str]) -> List[dict]:
    return [p for p in predictions if p.get("icd10_code") in kb_codes]
