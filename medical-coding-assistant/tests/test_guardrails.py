from src.guardrails import is_safe_note, constrain_to_kb

def test_short_note():
    ok, reason = is_safe_note("too short")
    assert ok is False

def test_constrain_to_kb():
    preds = [
        {"icd10_code": "A00", "score": 0.9},
        {"icd10_code": "ZZZ", "score": 0.1},
    ]
    out = constrain_to_kb(preds, {"A00"})
    assert len(out) == 1 and out[0]["icd10_code"] == "A00"
