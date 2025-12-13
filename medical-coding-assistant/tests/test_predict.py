from src.predict import Predictor

def test_predict_pipeline():
    p = Predictor()
    p.load()
    out = p.predict("Patient with chest pain, SOB, EKG ST elevation", top_k=3)
    assert "predictions" in out and "safety" in out
