import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from config import TESSERACT_CMD, POPPLER_PATH, ALLOWED_EXTENSIONS

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def ocr_image(pil_image):
    # basic OCR without heavy preprocessing for portability
    text = pytesseract.image_to_string(pil_image, config='--oem 3 --psm 6')
    return text


def ocr_pdf(path_to_pdf):
    images = convert_from_path(path_to_pdf, dpi=200, poppler_path=POPPLER_PATH)
    pages = []
    for img in images:
        pages.append(ocr_image(img))
    return "\n\n".join(pages)

def extract_structured(text):
    result = {"patient_info": {}, "labs": {}, "diagnoses": [], "medications": [], "raw_text": text}
    name = re.search(r"(?:Name|Patient Name)[:\-]\s*([A-Za-z\s]+)", text, re.IGNORECASE)
    age = re.search(r"Age[:\-]\s*(\d{1,3})", text, re.IGNORECASE)
    gender = re.search(r"(?:Sex|Gender)[:\-]\s*(Male|Female|M|F)", text, re.IGNORECASE)
    if name: result["patient_info"]["name"] = name.group(1).strip()
    if age: result["patient_info"]["age"] = int(age.group(1))
    if gender:
        g = gender.group(1).lower()
        result["patient_info"]["gender"] = "Male" if g.startswith("m") else "Female"
    bs = re.search(r"(?:blood sugar|glucose|fasting)[:\s]*([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
    if bs: result["labs"]["blood_sugar"] = float(bs.group(1))
    bp = re.search(r"\b(\d{2,3})\s*\/\s*(\d{2,3})\b", text)
    if bp:
        result["labs"]["systolic"] = int(bp.group(1)); result["labs"]["diastolic"] = int(bp.group(2))
    bmi = re.search(r"\bBMI[:\s]*([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
    if bmi: result["labs"]["bmi"] = float(bmi.group(1))
    meds = []
    for med in ["metformin","insulin","lisinopril","amlodipine","atorvastatin"]:
        if re.search(r"\b"+med+r"\b", text, re.IGNORECASE): meds.append(med)
    result["medications"] = meds
    for kw in ["diabetes","hypertension","obesity","heart failure","chronic kidney","liver"]:
        if re.search(r"\b"+kw+r"\b", text, re.IGNORECASE): result["diagnoses"].append(kw)
    return result
