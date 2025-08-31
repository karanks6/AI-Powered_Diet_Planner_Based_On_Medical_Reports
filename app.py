from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil

from modules.ocr_module import extract_text
from modules.nlp_extraction import extract_lab_values
from modules.condition_detector import detect_conditions
from modules.diet_recommender import recommend_foods
from modules.optimizer import optimize_day_plan

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_report(file: UploadFile, allergies: str = Form("")):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)


    # 1. OCR
    text = extract_text(file_path)


    # 2. NLP
    labs = extract_lab_values(text)


    # 3. Detect conditions
    conditions = detect_conditions(labs)


    # 4. Recommend foods
    allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]
    candidates = recommend_foods(conditions, allergy_list)


    # 5. Optimize daily plan
    servings, summary = optimize_day_plan(candidates)


    return JSONResponse({
        "labs": labs,
        "conditions": conditions,
        "diet_plan": servings,
        "nutrition_summary": summary
    })
