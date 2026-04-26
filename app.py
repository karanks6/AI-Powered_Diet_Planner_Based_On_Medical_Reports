import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.utils import secure_filename
from models.ocr_model import allowed_file, ocr_pdf, ocr_image, extract_structured
from models.nlp_model import analyze as nlp_analyze
from utils.nutrition import calculate_tdee, macro_split
from models.diet_logic import generate_plan as generate_diet_plan
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "your_secret_key"
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------------- INDEX PAGE ---------------------- #
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("report_file")
        if not file or file.filename == "":
            flash("No file selected.", "danger")
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("Invalid file type. Please upload a PDF or image file.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_path)

        ext = filename.rsplit(".", 1)[1].lower()
        if ext == "pdf":
            text = ocr_pdf(saved_path)
        else:
            pil_img = Image.open(saved_path).convert("RGB")
            text = ocr_image(pil_img)

        struct = extract_structured(text)
        session["ocr_struct"] = struct
        session["raw_text"] = text
        return redirect(url_for("analyze_report"))

    return render_template("index.html")


# ---------------------- ANALYZE REPORT ---------------------- #
@app.route("/analyze_report", methods=["GET", "POST"])
def analyze_report():
    struct = session.get("ocr_struct", {})
    if request.method == "POST":
        profile = {
            "age": int(request.form.get("age")),
            "weight": float(request.form.get("weight")),
            "height": float(request.form.get("height")),
            "gender": request.form.get("gender"),
            "activity": request.form.get("activity"),
            "dietary_pref": request.form.get("dietary_pref"),
            "regional_pref": request.form.get("regional_pref"),
            "plan_type": request.form.get("plan_type"),  # daily or weekly
        }

        profile["bmi"] = round(profile["weight"] / ((profile["height"] / 100.0) ** 2), 1)
        session["profile"] = profile
        return redirect(url_for("generate_plan"))

    return render_template("analyze.html", struct=struct)


# ---------------------- GENERATE DIET PLAN ---------------------- #
@app.route("/generate_plan")
def generate_plan():
    profile = session.get("profile")
    struct = session.get("ocr_struct", {})

    if not profile:
        flash("Please fill in your details first.", "warning")
        return redirect(url_for("index"))

    # Detect medical conditions
    nlp_result = nlp_analyze(struct)
    detected_conditions = {cond: val for cond, val in nlp_result.get("conditions", {}).items() if val >= 1.0}
    session["detected_conditions"] = detected_conditions

    # Calculate nutrition targets safely
    tdee = calculate_tdee(
        profile["gender"],
        profile["weight"],
        profile["height"],
        profile["age"],
        profile["activity"],
    )
    calories = int(round(tdee))
    macros = macro_split(calories)

    # ✅ Safe defaults for missing macros
    nutrition_targets = {
        "calories": calories,
        "protein": macros.get("protein", 0),
        "carbs": macros.get("carbs", 0),
        "fat": macros.get("fat", 0),
    }

    session["nutrition"] = nutrition_targets

    # Generate diet plan
    plan = generate_diet_plan(profile, nlp_result.get("conditions", {}), nutrition_targets)
    session["plan"] = plan

    return redirect(url_for("results"))


# ---------------------- RESULTS PAGE ---------------------- #
@app.route("/results")
def results():
    profile = session.get("profile")
    plan = session.get("plan")
    nutrition = session.get("nutrition", {"calories": 0, "protein": 0, "carbs": 0, "fat": 0})
    detected_conditions = session.get("detected_conditions", {})

    if not plan:
        flash("No plan generated yet.", "warning")
        return redirect(url_for("index"))

    condition_list = [cond.replace("_", " ").title() for cond, val in detected_conditions.items() if val >= 1.0]

    return render_template(
        "results.html",
        profile=profile,
        plan=plan,
        nutrition=nutrition,
        conditions=condition_list,
        plan_type=profile.get("plan_type", "daily"),
    )


# ---------------------- DOWNLOAD PLAN AS PDF ---------------------- #
@app.route("/download_plan")
def download_plan():
    plan = session.get("plan")
    profile = session.get("profile", {})
    if not plan:
        flash("Plan not found.", "danger")
        return redirect(url_for("index"))

    filename = f"diet_plan_{profile.get('age', 'user')}.pdf"
    path = os.path.join(OUTPUT_FOLDER, filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Personalized Diet Plan")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Age: {profile.get('age')} | Gender: {profile.get('gender')} | BMI: {profile.get('bmi')}")
    y -= 30

    for day, meals in plan.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{day}")
        y -= 20
        for meal in meals:
            c.setFont("Helvetica", 10)
            meal_line = f"- {meal['meal_time'].title()}: {meal['dish']} ({meal['serving']})"
            c.drawString(60, y, meal_line[:100])
            y -= 12
            if y < 60:
                c.showPage()
                y = height - 50
        y -= 10

    c.save()
    return send_file(path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True)
