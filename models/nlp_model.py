import re
from collections import defaultdict

MED_MAP = {
    "metformin": ("diabetes", 0.9),
    "insulin": ("diabetes", 0.98),
    "lisinopril": ("hypertension", 0.9),
}

def interpret_labs(labs):
    conds = {}
    bs = labs.get("blood_sugar")
    if bs is not None:
        if bs > 126: conds["diabetes"] = 0.95
        elif bs >= 110: conds["prediabetes"] = 0.6
    s = labs.get("systolic"); d = labs.get("diastolic")
    if s and d:
        if s >= 140 or d >= 90: conds["hypertension"] = 0.9
    bmi = labs.get("bmi")
    if bmi:
        if bmi >= 30: conds["obesity"] = 0.95
        elif bmi >= 25: conds["overweight"] = 0.6
    return conds

def analyze(structured_text):
    # Your medical NLP logic here
    # Example: detect conditions from text
    text = str(structured_text).lower()

    conditions = {
        "diabetes": 1.0 if "diabetes" in text or "sugar" in text else 0.0,
        "hypertension": 1.0 if "hypertension" in text or "blood pressure" in text else 0.0,
        "heart_disease": 1.0 if "cardiac" in text or "cholesterol" in text else 0.0,
        "kidney_disease": 1.0 if "creatinine" in text or "urea" in text else 0.0,
        "liver_disease": 1.0 if "bilirubin" in text or "fatty liver" in text else 0.0,
        "obesity": 1.0 if "obesity" in text or "bmi" in text else 0.0,
        "anemia": 1.0 if "hemoglobin" in text or "anemia" in text else 0.0,
        "thyroid_disorder": 1.0 if "tsh" in text or "thyroid" in text else 0.0
    }

    # Confidence values (simple binary for now, can expand later)
    detected = {k: v for k, v in conditions.items() if v > 0}

    return {
        "conditions": conditions,
        "detected_conditions": detected,
        "summary": f"{len(detected)} conditions detected."
    }
